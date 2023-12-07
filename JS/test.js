const express = require("express");
const bodyParser = require("body-parser");
const app = express();

// Include functions from previous code
const { main, getTextBlocks, processPage, saveToCSV } = require("./main");

app.use(bodyParser.json());

app.post("/process-bucket", async (req, res) => {
  try {
    const bucketName = req.body.bucketName;

    // Get all objects in the bucket
    const objects = await s3Client
      .listObjects({ Bucket: bucketName })
      .promise();

    // Extract text from all PDF files
    for (const object of objects.Contents) {
      if (!object.Key.endsWith(".pdf")) continue;

      console.log(`Processing file: ${object.Key}`);

      // Extract text blocks for each page
      const textBlocks = await getTextBlocks(bucketName, object.Key);

      // Process each page and extract data
      for (const pageBlocks of textBlocks) {
        await processPage(pageBlocks);
      }
    }

    // Save extracted data to CSV file
    await saveToCSV(extractedData, `output-${bucketName}.csv`);

    res.json({
      message: `PDF processing completed for bucket: ${bucketName}`,
      data: extractedData,
    });
  } catch (error) {
    res.status(500).json({
      message: `Error processing PDFs in bucket: ${bucketName}`,
      error,
    });
  }
});

app.listen(3000, () => console.log("API server listening on port 3000"));
