// Use Hugging Face for embeddings (FREE - no API key needed!)
import { Pinecone } from '@pinecone-database/pinecone';
import * as dotenv from 'dotenv';

dotenv.config();

const HF_API_URL = 'https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2';

// Generate embeddings using Hugging Face (384 dimensions for aunjai-knowledge)
async function generateEmbedding(text: string): Promise<number[]> {
  const response = await fetch(HF_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ inputs: text }),
  });
  
  if (!response.ok) {
    throw new Error(`HF API error: ${response.status}`);
  }
  
  const embedding = await response.json();
  return embedding[0]; // Returns 384-dim vector
}

// Save to Pinecone
async function saveToKnowledgeBase(id: string, text: string, metadata: any) {
  const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY! });
  const index = pc.index('aunjai-knowledge');
  
  console.log(`🔄 Generating embedding for: ${id}`);
  const embedding = await generateEmbedding(text);
  
  await index.upsert([{
    id,
    values: embedding,
    metadata: {
      text: text.substring(0, 1000), // Limit text size
      ...metadata,
      timestamp: new Date().toISOString(),
    }
  }]);
  
  console.log(`✅ Saved: ${id}`);
}

// Import from memory files
async function importMemoryFiles() {
  const files = [
    { path: 'SOUL.md', category: 'vision' },
    { path: 'IDENTITY.md', category: 'identity' },
    { path: 'AGENTS.md', category: 'agents' },
    { path: 'USER.md', category: 'user' },
    { path: 'TOOLS.md', category: 'tools' },
    { path: 'BOOTSTRAP.md', category: 'bootstrap' },
    { path: 'HEARTBEAT.md', category: 'safety' },
    { path: 'MEMORY.md', category: 'memory' },
  ];
  
  for (const file of files) {
    try {
      const content = await Bun.file(`./${file.path}`).text();
      
      // Split into chunks (max 500 chars each)
      const chunks = content.match(/[\s\S]{1,500}/g) || [content];
      
      for (let i = 0; i < chunks.length; i++) {
        const chunkId = `${file.path.replace('.md', '')}-chunk-${i}`;
        await saveToKnowledgeBase(chunkId, chunks[i], {
          source: file.path,
          category: file.category,
          chunkIndex: i,
        });
        
        // Rate limiting - wait 1 second between requests
        await new Promise(r => setTimeout(r, 1000));
      }
      
    } catch (error) {
      console.error(`❌ Error importing ${file.path}:`, error.message);
    }
  }
  
  console.log('\n🎉 Import complete!');
}

// Run import
// importMemoryFiles();

export { generateEmbedding, saveToKnowledgeBase, importMemoryFiles };
