// Pinecone SDK Configuration for Nong Unjai Project
// Updated: เชื่อมต่อกับ Index aunjai-knowledge
import { Pinecone } from '@pinecone-database/pinecone';

// Initialize Pinecone client
// ใส่ API Key ใน .env file: PINECONE_API_KEY=your-api-key
const pc = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY || '',
});

// ชื่อ index และ host ที่ใช้เก็บข้อมูล
const INDEX_NAME = process.env.PINECONE_INDEX_NAME || 'aunjai-knowledge';
const INDEX_HOST = process.env.PINECONE_INDEX_HOST || 'https://aunjai-knowledge-3ygam8j.svc.aped-4627-b74a.pinecone.io';
const NAMESPACE = process.env.PINECONE_NAMESPACE || 'highlights';

// เชื่อมต่อกับ index ที่มีอยู่แล้ว (ไม่สร้างใหม่)
export function getIndex() {
  // ใช้ host สำหรับเชื่อมต่อกับ index ที่มีอยู่
  return pc.index(INDEX_NAME).namespace(NAMESPACE);
}

// ฟังก์ชันอัพโหลดข้อมูลพร้อม embedding (เข้า namespace: highlights)
export async function upsertMemory(id: string, text: string, embedding: number[], metadata: any) {
  const index = getIndex();
  
  await index.upsert([{
    id,
    values: embedding,
    metadata: {
      text,
      ...metadata,
      timestamp: new Date().toISOString(),
    }
  }]);
  
  console.log(`✅ Memory upserted to ${NAMESPACE}: ${id}`);
}

// ฟังก์ชันค้นหาแบบ similarity search (ค้นหาใน namespace: highlights)
export async function searchMemory(queryEmbedding: number[], topK: number = 5) {
  const index = getIndex();
  
  const results = await index.query({
    vector: queryEmbedding,
    topK,
    includeMetadata: true,
  });
  
  return results.matches;
}

// ฟังก์ชันค้นหาพร้อม filter (ค้นหาใน namespace: highlights)
export async function searchMemoryWithFilter(
  queryEmbedding: number[], 
  filter: Record<string, any>,
  topK: number = 5
) {
  const index = getIndex();
  
  const results = await index.query({
    vector: queryEmbedding,
    topK,
    includeMetadata: true,
    filter,
  });
  
  return results.matches;
}

// ฟังก์ชันลบ memory (ใน namespace: highlights)
export async function deleteMemory(id: string) {
  const index = getIndex();
  await index.deleteOne(id);
  console.log(`🗑️ Memory deleted from ${NAMESPACE}: ${id}`);
}

// ฟังก์ชันลบหลาย records (ใน namespace: highlights)
export async function deleteManyMemories(ids: string[]) {
  const index = getIndex();
  await index.deleteMany(ids);
  console.log(`🗑️ Deleted ${ids.length} memories from ${NAMESPACE}`);
}

// ฟังก์ชัน list ทุก records (ดูสถิติของ namespace)
export async function listAllMemories() {
  const index = getIndex();
  const stats = await index.describeIndexStats();
  return stats;
}

// ฟังก์ชันดึง record ตาม ID
export async function fetchMemory(id: string) {
  const index = getIndex();
  const result = await index.fetch([id]);
  return result.records[id];
}

// ฟังก์ชันอัพเดท metadata โดยไม่เปลี่ยน embedding
export async function updateMetadata(id: string, metadata: any) {
  const record = await fetchMemory(id);
  if (!record) {
    throw new Error(`Record ${id} not found`);
  }
  
  const index = getIndex();
  await index.upsert([{
    id,
    values: record.values,
    metadata: {
      ...record.metadata,
      ...metadata,
      updatedAt: new Date().toISOString(),
    }
  }]);
  
  console.log(`✅ Metadata updated: ${id}`);
}

// ============================================
// Search Specialist: Parallel Hybrid Search
// ============================================

export interface SearchResult {
  source: 'memory' | 'pinecone';
  id: string;
  content: string;
  score: number;
  metadata: any;
  clip_url?: string;
  video_url?: string;
  start_time?: number;
  end_time?: number;
  transcript?: string;
  type?: string;
}

export interface ParallelSearchResults {
  text_results: SearchResult[];      // จาก MEMORY.md
  video_results: SearchResult[];     // จาก Pinecone
  combined: SearchResult[];          // รวมกันเรียงตาม score
}

/**
 * Search Specialist: Parallel Hybrid Search
 * ค้นหาพร้อมกันทั้งจาก MEMORY.md (ผ่าน memory_search) และ Pinecone
 * 
 * @param query - คำค้นหา
 * @param queryEmbedding - vector embedding ของคำค้นหา (ถ้ามี)
 * @param topK - จำนวนผลลัพธ์ที่ต้องการจากแหล่งละ
 * @returns ParallelSearchResults
 */
export async function parallelSearch(
  query: string,
  queryEmbedding?: number[],
  topK: number = 3
): Promise<ParallelSearchResults> {
  console.log(`🔍 Search Specialist: Parallel search for "${query}"`);
  
  // ถ้าไม่มี embedding ให้ใช้ text search แทน (fetch ทุก record แล้ว filter)
  const searchPromises: Promise<SearchResult[]>[] = [];
  
  // 1. ค้นหาใน Pinecone (video highlights)
  if (queryEmbedding && queryEmbedding.length > 0) {
    searchPromises.push(
      searchPineconeVideos(queryEmbedding, topK)
    );
  } else {
    // ถ้าไม่มี embedding ให้ค้นหาแบบ fetch all แล้ว filter (fallback)
    searchPromises.push(
      searchPineconeByKeyword(query, topK)
    );
  }
  
  // 2. ค้นหาใน MEMORY.md ผ่าน memory_search tool
  // หมายเหตุ: จะเรียก memory_search แยกต่างหากใน orchestrator
  
  const [videoResults] = await Promise.all(searchPromises);
  
  // รวมผลลัพธ์
  const combined = [...videoResults].sort((a, b) => b.score - a.score);
  
  console.log(`✅ Search complete: ${videoResults.length} videos from Pinecone`);
  
  return {
    text_results: [],  // จะถูกเติมโดย orchestrator ที่เรียก memory_search
    video_results: videoResults,
    combined: combined
  };
}

/**
 * ค้นหา video highlights ใน Pinecone โดยใช้ vector similarity
 */
async function searchPineconeVideos(
  queryEmbedding: number[],
  topK: number = 3
): Promise<SearchResult[]> {
  try {
    const index = getIndex();
    
    const results = await index.query({
      vector: queryEmbedding,
      topK,
      includeMetadata: true,
    });
    
    if (!results.matches) {
      return [];
    }
    
    return results.matches.map((match: any) => ({
      source: 'pinecone' as const,
      id: match.id,
      content: match.metadata?.transcript || match.metadata?.text || '',
      score: match.score || 0,
      metadata: match.metadata,
      clip_url: match.metadata?.clip_url,
      video_url: match.metadata?.video_url,
      start_time: match.metadata?.start_time,
      end_time: match.metadata?.end_time,
      transcript: match.metadata?.transcript,
      type: match.metadata?.type || 'highlight',
    }));
    
  } catch (error) {
    console.error('❌ Error searching Pinecone:', error);
    return [];
  }
}

/**
 * ค้นหาแบบ keyword-based (fallback เมื่อไม่มี embedding)
 * ดึง records มาแล้ว filter ด้วย keyword
 */
async function searchPineconeByKeyword(
  keyword: string,
  topK: number = 3
): Promise<SearchResult[]> {
  try {
    // ดึง list ของ vector IDs (ต้องมีการ list ก่อน)
    // หมายเหตุ: Pinecone ไม่มี list โดยตรง ต้องใช้วิธีอื่น
    // ในทางปฏิบัติควรใช้ embedding จริง หรือเก็บ index แยก
    
    console.log('⚠️  Keyword search not implemented - please provide embedding');
    return [];
    
  } catch (error) {
    console.error('❌ Error in keyword search:', error);
    return [];
  }
}

/**
 * ค้นหาเฉพาะ video ที่ตรงกับ intent และมี clip_url
 * ใช้สำหรับ 3-Filter System (Filter 3: Interest Match)
 */
export async function searchHighlightsOnly(
  queryEmbedding: number[],
  minScore: number = 0.7,
  topK: number = 3
): Promise<SearchResult[]> {
  const allResults = await searchPineconeVideos(queryEmbedding, topK * 2);
  
  // Filter เฉพาะที่มี clip_url และ score สูงพอ
  return allResults
    .filter(r => r.clip_url && r.score >= minScore)
    .slice(0, topK);
}

export { pc, INDEX_NAME, INDEX_HOST, NAMESPACE };
