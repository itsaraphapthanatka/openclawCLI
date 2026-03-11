// Pinecone SDK Configuration for Nong Unjai Project
import { Pinecone } from '@pinecone-database/pinecone';

// Initialize Pinecone client
// ใส่ API Key ใน .env file: PINECONE_API_KEY=your-api-key
const pc = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY || '',
});

// ชื่อ index ที่ใช้เก็บข้อมูล
const INDEX_NAME = 'unjai-memory';

// ฟังก์ชันสร้าง index (ถ้ายังไม่มี)
export async function createIndex() {
  try {
    await pc.createIndex({
      name: INDEX_NAME,
      dimension: 1536, // OpenAI embedding dimension
      metric: 'cosine',
      spec: {
        serverless: {
          cloud: 'aws',
          region: 'us-east-1'
        }
      }
    });
    console.log('✅ Index created successfully');
  } catch (error) {
    console.log('Index may already exist:', error.message);
  }
}

// ฟังก์ชันอัพโหลดข้อมูลพร้อม embedding
export async function upsertMemory(id: string, text: string, embedding: number[], metadata: any) {
  const index = pc.index(INDEX_NAME);
  
  await index.upsert([{
    id,
    values: embedding,
    metadata: {
      text,
      ...metadata,
      timestamp: new Date().toISOString(),
    }
  }]);
  
  console.log(`✅ Memory upserted: ${id}`);
}

// ฟังก์ชันค้นหาแบบ similarity search
export async function searchMemory(queryEmbedding: number[], topK: number = 5) {
  const index = pc.index(INDEX_NAME);
  
  const results = await index.query({
    vector: queryEmbedding,
    topK,
    includeMetadata: true,
  });
  
  return results.matches;
}

// ฟังก์ชันลบ memory
export async function deleteMemory(id: string) {
  const index = pc.index(INDEX_NAME);
  await index.deleteOne(id);
  console.log(`🗑️ Memory deleted: ${id}`);
}

// ฟังก์ชัน list ทุก records
export async function listAllMemories() {
  const index = pc.index(INDEX_NAME);
  const stats = await index.describeIndexStats();
  return stats;
}

export { pc, INDEX_NAME };
