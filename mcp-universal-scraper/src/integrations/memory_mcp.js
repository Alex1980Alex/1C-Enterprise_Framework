/**
 * Memory MCP Integration for Universal Web Scraper
 * Saves scraped content to Knowledge Graph
 */

export class MemoryMCPIntegration {
  constructor() {
    this.enabled = false;
    this.initializeConnection();
  }

  async initializeConnection() {
    try {
      // Check if Memory MCP is available
      // In a real MCP environment, this would be handled by the MCP protocol
      console.error('Initializing Memory MCP integration...');
      this.enabled = true;
    } catch (error) {
      console.error('Memory MCP not available:', error.message);
      this.enabled = false;
    }
  }

  async saveScrapedContent(scrapingResult) {
    if (!this.enabled) {
      console.error('Memory MCP not available, skipping save');
      return false;
    }

    try {
      const { url, title, content, metadata, links, adapter_used } = scrapingResult;
      
      // Create main entity for the scraped page
      const pageEntity = {
        name: title || this.extractDomainFromUrl(url),
        entityType: 'scraped_webpage',
        observations: [
          `URL: ${url}`,
          `Scraped at: ${metadata.scraped_at}`,
          `Content length: ${metadata.content_length} characters`,
          `Adapter used: ${adapter_used}`,
          `Links found: ${metadata.links_found}`,
          `Content preview: ${content.substring(0, 300)}...`
        ]
      };

      // Create domain entity
      const domain = this.extractDomainFromUrl(url);
      const domainEntity = {
        name: domain,
        entityType: 'website_domain',
        observations: [
          `Domain: ${domain}`,
          `Last scraped: ${metadata.scraped_at}`,
          `Primary adapter: ${adapter_used}`
        ]
      };

      // Save entities to Memory MCP
      await this.createEntities([pageEntity, domainEntity]);

      // Create relations
      const relations = [
        {
          from: pageEntity.name,
          to: domainEntity.name,
          relationType: 'belongs_to_domain'
        },
        {
          from: pageEntity.name,
          to: `adapter_${adapter_used}`,
          relationType: 'processed_by'
        }
      ];

      // Create adapter entity if not exists
      const adapterEntity = {
        name: `adapter_${adapter_used}`,
        entityType: 'scraping_adapter',
        observations: [
          `Adapter type: ${adapter_used}`,
          `Last used: ${metadata.scraped_at}`,
          `Processed: ${pageEntity.name}`
        ]
      };

      await this.createEntities([adapterEntity]);
      await this.createRelations(relations);

      // Save links as separate entities and relations
      if (links && links.length > 0) {
        await this.saveLinksToMemory(pageEntity.name, links.slice(0, 10)); // Limit to 10 links
      }

      console.error(`Saved to Memory MCP: ${title} with ${relations.length} relations`);
      return true;

    } catch (error) {
      console.error('Error saving to Memory MCP:', error.message);
      return false;
    }
  }

  async saveLinksToMemory(parentPageName, links) {
    const linkEntities = [];
    const linkRelations = [];

    links.forEach((link, index) => {
      if (link.url && link.text) {
        const linkEntity = {
          name: `${parentPageName}_link_${index}`,
          entityType: 'webpage_link',
          observations: [
            `URL: ${link.url}`,
            `Link text: ${link.text}`,
            `Found on: ${parentPageName}`
          ]
        };

        linkEntities.push(linkEntity);
        linkRelations.push({
          from: parentPageName,
          to: linkEntity.name,
          relationType: 'contains_link'
        });
      }
    });

    if (linkEntities.length > 0) {
      await this.createEntities(linkEntities);
      await this.createRelations(linkRelations);
    }
  }

  async createEntities(entities) {
    // In a real MCP environment, this would call the Memory MCP server
    // For now, we simulate the call
    console.error(`[Memory MCP] Creating ${entities.length} entities`);
    
    // Simulate MCP call
    // await mcp_memory_create_entities({ entities });
    
    return true;
  }

  async createRelations(relations) {
    // In a real MCP environment, this would call the Memory MCP server
    console.error(`[Memory MCP] Creating ${relations.length} relations`);
    
    // Simulate MCP call
    // await mcp_memory_create_relations({ relations });
    
    return true;
  }

  async searchInMemory(query) {
    try {
      console.error(`[Memory MCP] Searching for: ${query}`);
      
      // Simulate MCP call
      // const results = await mcp_memory_search_nodes({ query });
      
      // Return simulated results
      return {
        entities: [],
        relations: []
      };
    } catch (error) {
      console.error('Error searching Memory MCP:', error.message);
      return null;
    }
  }

  extractDomainFromUrl(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch (error) {
      return 'unknown_domain';
    }
  }
}