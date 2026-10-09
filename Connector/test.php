<?php
declare(strict_types=1);

require_once __DIR__ . '/connector.php';

$connectorVersion = OTA_CONNECTOR_VERSION;
$env = [
    'APP_ENV' => OTAEnv::get('APP_ENV', 'production'),
    'DB_DRIVER' => OTAEnv::get('DB_DRIVER', 'mysql'),
    'DB_HOST' => OTAEnv::get('DB_HOST', '127.0.0.1'),
    'DB_PORT' => OTAEnv::get('DB_PORT', '3306'),
    'DB_NAME' => OTAEnv::get('DB_NAME', ''),
    'DB_USER' => OTAEnv::get('DB_USER', ''),
    'ALLOWED_ORIGINS' => OTAEnv::get('ALLOWED_ORIGINS', ''),
];

$result = null;
$errorMessage = null;

try {
    $pdo = ota_connector_bootstrap_once();
    $result = ping_connection($pdo);
} catch (Throwable $e) {
    $result = [
        'success' => false,
        'version' => $connectorVersion,
        'checked_at' => gmdate('c'),
        'error' => $e->getMessage(),
    ];
    $errorMessage = $e->getMessage();
}

$driverLabel = $env['DB_DRIVER'] ?: 'unknown';
$dbLabel = $env['DB_NAME'] !== '' ? $env['DB_NAME'] : 'not set';
$hostLabel = ota_mask_string($env['DB_HOST'] ?: '127.0.0.1', 4);
$userLabel = ota_mask_string($env['DB_USER'] ?: 'unknown', 2);
$statusOk = (bool)($result['success'] ?? false);
$latency = $result['result']['latency_ms'] ?? null;
$alive = $result['result']['alive'] ?? false;
$checkedAt = $result['checked_at'] ?? gmdate('c');
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Connector Test | OnTrackAssets</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest"></script>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; min-height: 100%; }
  body {
    background:
      radial-gradient(circle at 10% 15%, rgba(11,11,11,.05), transparent 18%),
      radial-gradient(circle at 90% 10%, rgba(11,11,11,.05), transparent 16%),
      #F2F3F4;
    color: #0B0B0B;
    font-family: Inter, sans-serif;
    padding: 28px;
  }
  .wrap { max-width: 1280px; margin: 0 auto; }
  .hero {
    border-radius: 28px;
    background: linear-gradient(180deg, rgba(255,255,255,.96), rgba(255,255,255,.82));
    border: 1px solid rgba(11,11,11,.08);
    box-shadow: 0 18px 50px rgba(11,11,11,.08);
    padding: 28px;
    display: grid;
    grid-template-columns: 1.2fr .8fr;
    gap: 18px;
    align-items: stretch;
  }
  .badge {
    display: inline-flex; align-items: center; gap: 8px;
    border-radius: 999px; background: rgba(11,11,11,.06);
    border: 1px solid rgba(11,11,11,.08); padding: 8px 14px;
    font-size: .74rem; font-weight: 900; letter-spacing: .14em; text-transform: uppercase;
    width: fit-content;
  }
  h1 {
    margin: 14px 0 10px;
    font-family: Montserrat, sans-serif;
    font-size: clamp(2rem, 3vw, 3.2rem);
    letter-spacing: -.05em;
    line-height: 1.05;
  }
  p.lead { margin: 0; color: #555; line-height: 1.8; max-width: 900px; }
  .card {
    border-radius: 22px;
    background: #fff;
    border: 1px solid rgba(11,11,11,.08);
    box-shadow: 0 12px 30px rgba(11,11,11,.06);
    padding: 18px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 18px;
  }
  .mini {
    padding: 16px;
    border-radius: 18px;
    background: #F8F9FA;
    border: 1px solid rgba(11,11,11,.08);
  }
  .mini span {
    display: block;
    font-size: .68rem;
    text-transform: uppercase;
    letter-spacing: .14em;
    color: #64748B;
    margin-bottom: 6px;
    font-weight: 800;
  }
  .mini strong {
    font-family: Montserrat, sans-serif;
    font-size: 1rem;
  }
  .status {
    border-radius: 22px;
    padding: 22px;
    color: #fff;
    background: linear-gradient(180deg, #0B0B0B, #161616);
    border: 1px solid rgba(255,255,255,.06);
    box-shadow: 0 18px 40px rgba(0,0,0,.22);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 16px;
  }
  .status.ok { background: linear-gradient(180deg, #0f3d26, #08150f); }
  .status.bad { background: linear-gradient(180deg, #5b1111, #220707); }
  .status-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
  }
  .pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 999px;
    padding: 8px 12px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.08);
    font-size: .8rem;
    font-weight: 800;
  }
  .status-title {
    margin: 0;
    font-family: Montserrat, sans-serif;
    font-size: 1.2rem;
    letter-spacing: -.03em;
  }
  .status-desc {
    margin: 0;
    color: rgba(255,255,255,.74);
    line-height: 1.75;
    font-size: .93rem;
  }
  .actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  .btn {
    border: 1px solid #0B0B0B;
    border-radius: 14px;
    padding: 13px 18px;
    font-family: Montserrat, sans-serif;
    font-size: .84rem;
    font-weight: 900;
    letter-spacing: .08em;
    text-transform: uppercase;
    cursor: pointer;
    transition: .2s ease;
  }
  .btn.primary { background: #0B0B0B; color: #F2F3F4; }
  .btn.secondary { background: transparent; color: #0B0B0B; }
  .btn:hover { transform: translateY(-2px); }
  .log {
    margin-top: 18px;
    border-radius: 22px;
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(11,11,11,.08);
    box-shadow: 0 12px 30px rgba(11,11,11,.05);
    padding: 20px;
  }
  .log pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: .88rem;
    line-height: 1.7;
    color: #222;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 18px;
    overflow: hidden;
    border-radius: 18px;
    background: #fff;
    border: 1px solid rgba(11,11,11,.08);
  }
  th, td {
    text-align: left;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(11,11,11,.06);
    vertical-align: top;
    font-size: .92rem;
  }
  th {
    background: #F8F9FA;
    font-family: Montserrat, sans-serif;
    font-size: .76rem;
    text-transform: uppercase;
    letter-spacing: .12em;
    color: #64748B;
  }
  tr:last-child td { border-bottom: none; }
  @media (max-width: 980px) { .hero { grid-template-columns: 1fr; } }
  @media (max-width: 720px) {
    body { padding: 16px; }
    .grid { grid-template-columns: 1fr; }
    .actions { flex-direction: column; }
    .btn { width: 100%; }
  }
</style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div>
        <div class="badge"><i data-lucide="plug-zap" style="width:14px;height:14px;"></i> Connector Test</div>
        <h1>Secure database connector health check</h1>
        <p class="lead">
          This page loads the connector, opens the database securely, and runs a ping check so you can confirm the infrastructure is ready before wiring APIs and services on top of it.
        </p>

        <div class="grid">
          <div class="mini">
            <span>Connector Version</span>
            <strong><?= htmlspecialchars($connectorVersion) ?></strong>
          </div>
          <div class="mini">
            <span>Checked At</span>
            <strong><?= htmlspecialchars($checkedAt) ?></strong>
          </div>
          <div class="mini">
            <span>Database</span>
            <strong><?= htmlspecialchars($dbLabel) ?></strong>
          </div>
          <div class="mini">
            <span>Driver</span>
            <strong><?= htmlspecialchars($driverLabel) ?></strong>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Field</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Environment</td><td><?= htmlspecialchars($env['APP_ENV']) ?></td></tr>
            <tr><td>Host</td><td><?= htmlspecialchars($hostLabel) ?></td></tr>
            <tr><td>Database User</td><td><?= htmlspecialchars($userLabel) ?></td></tr>
            <tr><td>Allowed Origins</td><td><?= htmlspecialchars($env['ALLOWED_ORIGINS'] !== '' ? $env['ALLOWED_ORIGINS'] : 'Not configured') ?></td></tr>
          </tbody>
        </table>

        <div class="actions">
          <button class="btn primary" id="runPing" type="button">Run Ping Again</button>
          <button class="btn secondary" id="copyJson" type="button">Copy JSON Result</button>
        </div>
      </div>

      <aside class="status <?= $statusOk ? 'ok' : 'bad' ?>" id="statusCard">
        <div class="status-top">
          <div class="pill">
            <i data-lucide="<?= $statusOk ? 'shield-check' : 'shield-x' ?>" style="width:14px;height:14px;"></i>
            <?= $statusOk ? 'Connection Healthy' : 'Connection Failed' ?>
          </div>
          <div class="pill">
            <i data-lucide="timer" style="width:14px;height:14px;"></i>
            <?= htmlspecialchars((string)($latency ?? 'n/a')) ?> ms
          </div>
        </div>

        <div>
          <h2 class="status-title"><?= $alive ? 'Database responded successfully.' : 'Database did not respond.' ?></h2>
          <p class="status-desc">
            <?php if ($statusOk): ?>
              The connector loaded correctly, the PDO connection opened, and the ping check returned a live response.
            <?php else: ?>
              The connector loaded, but the ping check could not complete successfully. Review your environment variables, database credentials, and network access.
            <?php endif; ?>
          </p>
        </div>

        <div class="card">
          <div style="font-family:Montserrat,sans-serif;font-size:.76rem;font-weight:900;letter-spacing:.12em;text-transform:uppercase;color:#64748B;margin-bottom:10px;">Raw Result</div>
          <div style="font-size:.92rem;line-height:1.7;word-break:break-word;">
            <strong>Success:</strong> <?= $statusOk ? 'true' : 'false' ?><br>
            <strong>Version:</strong> <?= htmlspecialchars((string)($result['version'] ?? $connectorVersion)) ?><br>
            <strong>Latency:</strong> <?= htmlspecialchars((string)($latency ?? 'n/a')) ?> ms
          </div>
        </div>
      </aside>
    </section>

    <div class="log">
      <pre id="jsonResult"><?= htmlspecialchars(json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), ENT_QUOTES, 'UTF-8') ?></pre>
    </div>
  </div>

  <script>
    if (window.lucide) window.lucide.createIcons();

    const jsonResult = <?= json_encode($result, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) ?>;

    document.getElementById('runPing').addEventListener('click', async () => {
      const url = new URL(window.location.href);
      url.searchParams.set('refresh', String(Date.now()));
      window.location.href = url.toString();
    });

    document.getElementById('copyJson').addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(JSON.stringify(jsonResult, null, 2));
      } catch (e) {}
    });
  </script>
</body>
</html>
