#!/usr/bin/env node

/**
 * OCR Service using Tesseract.js
 * Usage: node ocr_service.js <image_path_or_url>
 */

const { createWorker } = require('tesseract.js');
const fs = require('fs');
const https = require('https');
const http = require('http');
const { URL } = require('url');

/**
 * Download image from URL
 */
async function downloadImage(url) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;

    protocol.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download image: HTTP ${response.statusCode}`));
        return;
      }

      const chunks = [];
      response.on('data', (chunk) => chunks.push(chunk));
      response.on('end', () => resolve(Buffer.concat(chunks)));
      response.on('error', reject);
    }).on('error', reject);
  });
}

/**
 * Perform OCR on image
 */
async function performOCR(imageSource) {
  const worker = await createWorker('chi_sim+eng', 1, {
    logger: m => {
      // Only log progress for debugging
      if (m.status === 'recognizing text') {
        process.stderr.write(`\rProgress: ${Math.round(m.progress * 100)}%`);
      }
    }
  });

  try {
    let imageData;

    // Check if input is URL or file path
    if (imageSource.startsWith('http://') || imageSource.startsWith('https://')) {
      console.error('Downloading image from URL...');
      imageData = await downloadImage(imageSource);
    } else {
      // Read from file
      if (!fs.existsSync(imageSource)) {
        throw new Error(`File not found: ${imageSource}`);
      }
      imageData = fs.readFileSync(imageSource);
    }

    console.error('\nPerforming OCR...');
    const { data: { text } } = await worker.recognize(imageData);

    await worker.terminate();

    return text.trim();
  } catch (error) {
    await worker.terminate();
    throw error;
  }
}

// Main execution
(async () => {
  try {
    // Check command line arguments
    if (process.argv.length < 3) {
      console.error('Usage: node ocr_service.js <image_path_or_url>');
      process.exit(1);
    }

    const imageSource = process.argv[2];

    // Perform OCR
    const text = await performOCR(imageSource);

    // Output result as JSON
    console.log(JSON.stringify({
      success: true,
      text: text,
      length: text.length
    }));

    process.exit(0);
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message
    }));
    process.exit(1);
  }
})();
