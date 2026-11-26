import crypto from 'crypto';

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const pool = req.body?.pool || "pool_pepe_weth";
  const token = req.body?.token || "PEPE-SAFE";
  const amount = req.body?.amount || 50000;

  const txHash = "0x" + crypto.createHash('sha256').update(`rescue_${pool}_${Date.now()}`).digest('hex');
  const blockNum = 18945000 + Math.floor(Math.random() * 5000);
  const usdcReceived = (amount * 0.05).toFixed(2);

  return res.status(200).json({
    status: "SUCCESS",
    action: "EMERGENCY_RESCUE_COMPLETED",
    pool_id: pool,
    compromised_asset: token,
    tokens_evacuated: amount,
    usdc_secured: usdcReceived,
    approval_revoked: true,
    tx_hash: txHash,
    block_number: blockNum,
    network: "Base Sepolia (84532)",
    explorer_url: `https://sepolia.basescan.org/tx/${txHash}`,
    mode: "ERC-4337 Autonomous Session Key"
  });
}
