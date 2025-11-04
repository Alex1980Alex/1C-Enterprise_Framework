/**
 * Docling MCP Integration for Universal Web Scraper
 * Handles document conversion (PDF, DOCX, etc.) to Markdown
 */

export class DoclingMCPIntegration {
  constructor() {
    this.enabled = false;
    this.supportedFormats = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls'];
    this.initializeConnection();
  }

  async initializeConnection() {
    try {
      console.error('Initializing Docling MCP integration...');
      this.enabled = true;
    } catch (error) {
      console.error('Docling MCP not available:', error.message);
      this.enabled = false;
    }
  }

  isDocumentUrl(url) {
    try {
      const urlPath = new URL(url).pathname.toLowerCase();
      return this.supportedFormats.some(format => urlPath.endsWith(format));
    } catch (error) {
      return false;
    }
  }

  async convertDocument(url, options = {}) {
    if (!this.enabled) {
      throw new Error('Docling MCP not available');
    }

    if (!this.isDocumentUrl(url)) {
      throw new Error(`Unsupported document format. Supported: ${this.supportedFormats.join(', ')}`);
    }

    try {
      console.error(`Converting document with Docling: ${url}`);

      // Determine document type
      const docType = this.getDocumentType(url);
      
      // Configure conversion options based on document type
      const conversionOptions = {
        input_path: url,
        extract_images: options.extract_images !== false,
        ocr_enabled: options.ocr_enabled !== false,
        ...options
      };

      // In a real MCP environment, this would call the Docling MCP server
      const conversionResult = await this.callDoclingMCP(conversionOptions);

      // Process the result
      const processedResult = {
        url,
        title: this.extractTitleFromPath(url),
        content: conversionResult.markdown_content,
        metadata: {
          original_format: docType,
          converted_at: new Date().toISOString(),
          content_length: conversionResult.markdown_content.length,
          conversion_method: 'docling_mcp',
          images_extracted: conversionResult.images_count || 0,
          tables_extracted: conversionResult.tables_count || 0,
          pages_processed: conversionResult.pages_count || 1
        },
        images: conversionResult.images || [],
        tables: conversionResult.tables || [],
        conversion_success: true
      };

      console.error(`Document converted successfully: ${processedResult.metadata.content_length} characters`);
      return processedResult;

    } catch (error) {
      console.error(`Error converting document ${url}:`, error.message);
      
      return {
        url,
        title: this.extractTitleFromPath(url),
        content: `Error converting document: ${error.message}`,
        metadata: {
          original_format: this.getDocumentType(url),
          converted_at: new Date().toISOString(),
          conversion_method: 'docling_mcp',
          conversion_success: false,
          error: error.message
        },
        images: [],
        tables: [],
        conversion_success: false
      };
    }
  }

  async callDoclingMCP(options) {
    // Simulate Docling MCP call
    // In real implementation: await mcp_docling_convert_document(options)
    
    console.error(`[Docling MCP] Converting: ${options.input_path}`);
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return simulated result
    return {
      markdown_content: `# Document Converted by Docling MCP\n\n**Original URL:** ${options.input_path}\n\n**Conversion Details:**\n- Format detected automatically\n- OCR enabled: ${options.ocr_enabled}\n- Images extracted: ${options.extract_images}\n\n**Content:**\n\nThis is simulated converted content from the document. In a real implementation, this would contain the actual extracted and converted text from the PDF/DOCX/etc. file.\n\n## Tables and Data\n\nAny tables and structured data would be converted to Markdown format here.\n\n## Images\n\nImage references and descriptions would be included here.`,
      images_count: options.extract_images ? 2 : 0,
      tables_count: 1,
      pages_count: 5,
      images: options.extract_images ? [
        { url: 'extracted_image_1.png', alt: 'Chart from document' },
        { url: 'extracted_image_2.png', alt: 'Diagram from document' }
      ] : [],
      tables: [
        { content: '| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |' }
      ]
    };
  }

  getDocumentType(url) {
    try {
      const urlPath = new URL(url).pathname.toLowerCase();
      
      if (urlPath.endsWith('.pdf')) return 'pdf';
      if (urlPath.endsWith('.docx') || urlPath.endsWith('.doc')) return 'word';
      if (urlPath.endsWith('.pptx') || urlPath.endsWith('.ppt')) return 'powerpoint';
      if (urlPath.endsWith('.xlsx') || urlPath.endsWith('.xls')) return 'excel';
      
      return 'unknown';
    } catch (error) {
      return 'unknown';
    }
  }

  extractTitleFromPath(url) {
    try {
      const urlPath = new URL(url).pathname;
      const filename = urlPath.split('/').pop();
      return filename.replace(/\.[^/.]+$/, ''); // Remove extension
    } catch (error) {
      return 'Converted Document';
    }
  }

  async batchConvertDocuments(urls, options = {}) {
    if (!this.enabled) {
      throw new Error('Docling MCP not available');
    }

    const results = [];
    const concurrentLimit = options.concurrent_limit || 2;
    const semaphore = new Semaphore(concurrentLimit);

    console.error(`Starting batch conversion of ${urls.length} documents`);

    const promises = urls.map(async (url, index) => {
      await semaphore.acquire();
      
      try {
        if (options.delay_between_conversions && index > 0) {
          await new Promise(resolve => setTimeout(resolve, options.delay_between_conversions * 1000));
        }

        const result = await this.convertDocument(url, options);
        results.push(result);
        
        console.error(`Converted ${index + 1}/${urls.length}: ${url}`);
      } catch (error) {
        console.error(`Failed to convert ${url}:`, error.message);
        results.push({
          url,
          conversion_success: false,
          error: error.message
        });
      } finally {
        semaphore.release();
      }
    });

    await Promise.all(promises);
    
    const successful = results.filter(r => r.conversion_success).length;
    console.error(`Batch conversion completed: ${successful}/${urls.length} successful`);
    
    return results;
  }

  async analyzeDocument(url) {
    if (!this.isDocumentUrl(url)) {
      throw new Error('Not a supported document format');
    }

    try {
      console.error(`Analyzing document structure: ${url}`);

      // In real implementation: await mcp_docling_analyze_document_structure
      const analysisResult = {
        url,
        document_type: this.getDocumentType(url),
        estimated_pages: this.estimatePages(url),
        contains_images: true,
        contains_tables: true,
        text_heavy: true,
        processing_recommendations: [
          'Enable OCR for scanned content',
          'Extract images for complete content',
          'Process tables as structured data'
        ],
        estimated_processing_time: '30-60 seconds'
      };

      return analysisResult;

    } catch (error) {
      console.error(`Error analyzing document ${url}:`, error.message);
      throw error;
    }
  }

  estimatePages(url) {
    // Simple heuristic based on URL patterns
    const urlStr = url.toLowerCase();
    
    if (urlStr.includes('manual') || urlStr.includes('guide')) return '10-50';
    if (urlStr.includes('report') || urlStr.includes('specification')) return '5-20';
    if (urlStr.includes('presentation')) return '10-30';
    
    return '1-10';
  }

  getSupportedFormats() {
    return {
      formats: this.supportedFormats,
      capabilities: {
        pdf: ['OCR', 'Text extraction', 'Image extraction', 'Table extraction'],
        word: ['Text extraction', 'Image extraction', 'Table extraction', 'Formatting preservation'],
        powerpoint: ['Slide extraction', 'Image extraction', 'Text extraction'],
        excel: ['Sheet extraction', 'Data extraction', 'Chart extraction']
      },
      limitations: [
        'Password-protected documents require credentials',
        'Very large files (>100MB) may take longer to process',
        'Complex layouts may need manual review'
      ]
    };
  }
}

// Simple semaphore for rate limiting
class Semaphore {
  constructor(maxConcurrency) {
    this.maxConcurrency = maxConcurrency;
    this.currentConcurrency = 0;
    this.queue = [];
  }

  async acquire() {
    if (this.currentConcurrency < this.maxConcurrency) {
      this.currentConcurrency++;
      return;
    }

    return new Promise((resolve) => {
      this.queue.push(resolve);
    });
  }

  release() {
    this.currentConcurrency--;
    if (this.queue.length > 0) {
      const resolve = this.queue.shift();
      this.currentConcurrency++;
      resolve();
    }
  }
}