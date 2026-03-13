#!/usr/bin/env node
/**
 * Example: Auto-save conversation to Pinecone
 * ตัวอย่างการใช้งานเก็บบทสนทนาอัตโนมัติ
 */

const { saveConversation, saveMessage, searchMemory } = require('./pinecone-auto-save.cjs');

// ตัวอย่าง: เก็บบทสนทนา
async function example() {
  
  // 1. เก็บทีละข้อความ
  console.log('=== บันทึกทีละข้อความ ===');
  await saveMessage('001', 'user', 'สวัสดี น้องอุ่นใจ', { user: 'Kurosaji' });
  await saveMessage('002', 'assistant', 'สวัสดีค่ะคุณพี่! ยินดีที่ได้รู้จักค่ะ', { user: 'Kurosaji' });
  await saveMessage('003', 'user', 'ช่วยสร้าง dashboard ให้หน่อย', { user: 'Kurosaji', topic: 'dashboard' });
  
  // 2. เก็บทั้งบทสนทนา
  console.log('\n=== บันทึกทั้งบทสนทนา ===');
  const messages = [
    { role: 'user', content: 'อยากรู้เรื่อง Pinecone', source: 'chat' },
    { role: 'assistant', content: 'Pinecone คือ vector database ค่ะ', source: 'chat' },
    { role: 'user', content: 'ช่วยติดตั้งให้หน่อย', source: 'chat' },
    { role: 'assistant', content: 'ได้ค่ะ! ติดตั้งให้แล้ว', source: 'chat' }
  ];
  await saveConversation('session-001', messages);
  
  // 3. ค้นหาความจำ
  console.log('\n=== ค้นหาความจำ ===');
  const results = await searchMemory('dashboard', 3);
  console.log(`พบ ${results.matches.length} ผลลัพธ์:`);
  results.matches.forEach((m, i) => {
    console.log(`${i+1}. ${m.metadata.text.substring(0, 60)}... (score: ${m.score.toFixed(3)})`);
  });
}

// Run
// example().catch(console.error);

module.exports = { example };
