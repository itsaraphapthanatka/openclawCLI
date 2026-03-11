// ตัวอย่างการใช้งาน Pinecone SDK กับ Nong Unjai
import { 
  createIndex, 
  upsertMemory, 
  searchMemory, 
  deleteMemory,
  listAllMemories 
} from './pinecone-config';

// ตัวอย่างการใช้งาน
async function example() {
  // 1. สร้าง index (ทำครั้งแรกครั้งเดียว)
  await createIndex();
  
  // 2. บันทึกความจำ (ต้องมี embedding จาก OpenAI หรือ service อื่น)
  const embedding = [0.1, 0.2, 0.3, /* ... 1536 ตัว */]; 
  await upsertMemory(
    'memory-001',
    'คุณพี่ Thanasit ชอบคุยเรื่อง dashboard',
    embedding,
    { user: 'Thanasit', type: 'preference' }
  );
  
  // 3. ค้นหาความจำที่คล้ายกัน
  const queryEmbedding = [0.1, 0.2, 0.3, /* ... */];
  const results = await searchMemory(queryEmbedding, 3);
  console.log('🔍 Search results:', results);
  
  // 4. ดูสถิติ
  const stats = await listAllMemories();
  console.log('📊 Index stats:', stats);
  
  // 5. ลบความจำ
  // await deleteMemory('memory-001');
}

// Run example
// example().catch(console.error);
