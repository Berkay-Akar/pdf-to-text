const AWS = require("aws-sdk");
const PDFDocument = require("pdf-lib").PDFDocument;
const csvWriter = require("csv-writer");

const bucketName = process.env.AWS_BUCKET_NAME;
const accessKey = process.env.AWS_ACCESS_KEY_ID;
const secretKey = process.env.AWS_SECRET_ACCESS_KEY;
const region = process.env.AWS_REGION_NAME;

// Configure AWS SDK with credentials and region
AWS.config.update({
  accessKeyId: accessKey,
  secretAccessKey: secretKey,
  region: region,
});

// Create clients for S3 and Textract
const s3Client = new AWS.S3();
const textractClient = new AWS.Textract();

const extractedData = [];

async function main() {
  // Get all objects in the bucket
  const objects = await s3Client.listObjects({ Bucket: bucketName }).promise();

  for (const object of objects.Contents) {
    // Skip non-PDF files
    if (!object.Key.endsWith(".pdf")) continue;

    console.log(`Processing file: ${object.Key}`);

    // Download the PDF file
    const fileData = await s3Client
      .getObject({ Bucket: bucketName, Key: object.Key })
      .promise();

    // Load the PDF document
    const pdfDoc = await PDFDocument.load(fileData.Body);

    // Get the number of pages
    const pageCount = pdfDoc.getPageCount();

    // Process each page of the PDF
    for (let i = 1; i <= pageCount; i++) {
      const textBlocks = await getTextBlocks(object.Key, i);
      await processPage(textBlocks);
    }
  }

  // Save extracted data to CSV file
  await saveToCSV(extractedData, "output.csv");
}

async function getTextBlocks(fileName, pageNumber) {
  const response = await textractClient
    .detectDocumentText({
      Document: {
        S3Object: {
          Bucket: bucketName,
          Name: fileName,
        },
      },
    })
    .promise();

  return response.Blocks.filter(
    (block) => block.BlockType !== "PAGE" && block.Page === pageNumber
  );
}

async function processPage(textBlocks) {
  for (const block of textBlocks) {
    console.log(`Detected: ${block.Text}`);
    console.log(`Confidence: ${block.Confidence.toFixed(2)}%`);

    // Extract words with #
    if (block.Text.includes("#")) {
      const words = block.Text.split(/\s+/);
      for (const word of words) {
        if (word.includes("#")) {
          extractedData.push({
            word,
            file: block.Page,
            confidence: block.Confidence.toFixed(2) + "%",
          });
        }
      }
    }
  }
}

async function saveToCSV(data, filePath) {
  const writer = csvWriter.createObjectCsvWriter({
    path: filePath,
    header: ["word", "file", "confidence"],
  });
  await writer.writeRecords(data);
}

main().catch((error) => console.error(error));
