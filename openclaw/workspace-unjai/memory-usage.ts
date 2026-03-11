// ตัวอย่าง: บันทึกและค้นหาความจำ
import { Pinecone } from '@pinecone-database/pinecone';

const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY! });
const index = pc.index('unjai-memory');

// === 1. บันทึกความจำ ===
// ต้องมี embedding จาก OpenAI ก่อน (1536 dimensions)
async function saveMemory(id: string, text: string, embedding: number[], metadata: any) {
  await index.upsert([{
    id,
    values: embedding,
    metadata: {
      text,
      ...metadata,
      timestamp: new Date().toISOString(),
    }
  }]);
  console.log(`💾 Saved: ${id}`);
}

// === 2. ค้นหาความจำ ===
async function searchMemory(queryEmbedding: number[], topK: number = 3) {
  const results = await index.query({
    vector: queryEmbedding,
    topK,
    includeMetadata: true,
  });
  return results.matches;
}

// === 3. ตัวอย่างใช้งานจริง ===
async function example() {
  // สมมติมี embedding จาก OpenAI
  const mockEmbedding = new Array(1536).fill(0).map(() => Math.random() - 0.5);
  
  // บันทึก
  await saveMemory(
    'msg-001', 
    'คุณพี่ Thanasit ชอบ dashboard สี pastel',
    mockEmbedding,
    { user: 'Thanasit', topic: 'dashboard' }
  );
  
  // ค้นหา
  const queryEmbedding = new Array(1536).fill(0).map(() => Math.random() - 0.5);
  const memories = await searchMemory(queryEmbedding, 5);
  
  console.log('🔍 Found memories:');
  memories.forEach(m => {
    console.log(`- ${m.metadata?.text} (score: ${m.score?.toFixed(3)})`);
  });
}

// example();

export { saveMemory, searchMemory };
