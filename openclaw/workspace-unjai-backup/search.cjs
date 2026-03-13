require('dotenv').config();

async function search(query) {
  const API_KEY = process.env.PINECONE_API_KEY;
  
  // Get index host
  const controlResp = await fetch('https://api.pinecone.io/indexes', {
    headers: { 'Api-Key': API_KEY }
  });
  const indexes = await controlResp.json();
  const index = indexes.indexes.find(i => i.name === 'aunjai-knowledge');
  
  // Generate query embedding (same method as import)
  const vector = new Array(384).fill(0);
  for (let i = 0; i < query.length; i++) {
    const char = query.charCodeAt(i);
    vector[i % 384] += (char % 100) / 100;
  }
  const mag = Math.sqrt(vector.reduce((s, v) => s + v * v, 0));
  const normalized = vector.map(v => v / (mag || 1));
  
  // Search
  const resp = await fetch(`https://${index.host}/query`, {
    method: 'POST',
    headers: {
      'Api-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      vector: normalized,
      topK: 5,
      includeMetadata: true
    })
  });
  
  const result = await resp.json();
  
  console.log(`🔍 Search: "${query}"\n`);
  result.matches.forEach((m, i) => {
    console.log(`${i+1}. [${m.id}] Score: ${m.score.toFixed(3)}`);
    console.log(`   ${m.metadata.text.substring(0, 100)}...\n`);
  });
}

const query = process.argv[2] || 'dashboard';
search(query);
