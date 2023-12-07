const express = require("express");
const bodyParser = require("body-parser");
const app = express();

// Include the main function from previous code
const main = require("./main");

app.use(bodyParser.json());

app.post("/process-pdf", async (req, res) => {
  try {
    // Get file data from request body
    const { bucketName, fileName } = req.body;

    // Extract text blocks and process page
    const textBlocks = await getTextBlocks(bucketName, fileName);
    await processPage(textBlocks);

    // Respond with extracted data
    res.json({
      message: "PDF processing successful",
      data: extractedData,
    });
  } catch (error) {
    res.status(500).json({
      message: "Error processing PDF",
      error,
    });
  }
});

app.listen(3000, () => console.log("API server listening on port 3000"));
