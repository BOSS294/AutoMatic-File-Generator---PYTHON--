<?php
declare(strict_types=1);

/**
 * OnTrackAssets Developer Console API Tester
 * Place this file in the same directory as connector.php and DeveloperConsoleApi/
 */

require_once __DIR__ . '/connector.php';

header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('Referrer-Policy: strict-origin-when-cross-origin');

if (PHP_SAPI !== 'cli') {
    $allowedOrigins = [];
    try {
        $allowedOrigins = OTASecurity::allowedOrigins();
    } catch (Throwable $e) {
        $allowedOrigins = [];
    }

    $origin = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
    if ($origin !== '' && $allowedOrigins !== []) {
        $ok = false;
        foreach ($allowedOrigins as $allowedOrigin) {
            if (OTASecurity::originMatches($origin, $allowedOrigin)) {
                $ok = true;
                break;
            }
        }
        if (!$ok) {
            http_response_code(403);
            echo 'Origin not allowed.';
            exit;
        }
    }
}

function ota_api_url(string $path): string
{
    $path = ltrim($path, '/');
    return $path;
}

function ota_api_request(string $method, string $url, ?array $payload = null, array $headers = []): array
{
    $ch = curl_init($url);
    if ($ch === false) {
        return [
            'ok' => false,
            'status' => 0,
            'error' => 'Unable to initialize cURL.',
            'body' => null,
            'json' => null,
        ];
    }

    $method = strtoupper($method);
    $finalHeaders = array_merge([
        'Accept: application/json',
    ], $headers);

    if ($method === 'POST') {
        $body = $payload === null ? '{}' : json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $finalHeaders[] = 'Content-Type: application/json';
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $body,
        ]);
    } elseif ($method !== 'GET') {
        curl_setopt_array($ch, [
            CURLOPT_CUSTOMREQUEST => $method,
        ]);
        if ($payload !== null) {
            $finalHeaders[] = 'Content-Type: application/json';
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
        }
    }

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_HTTPHEADER => $finalHeaders,
        CURLOPT_HEADER => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
    ]);

    $response = curl_exec($ch);
    $errno = curl_errno($ch);
    $error = curl_error($ch);
    $info = curl_getinfo($ch);
    curl_close($ch);

    if ($response === false || $errno !== 0) {
        return [
            'ok' => false,
            'status' => 0,
            'error' => $error ?: 'Request failed.',
            'body' => null,
            'json' => null,
        ];
    }

    $headerSize = (int)($info['header_size'] ?? 0);
    $rawHeaders = substr($response, 0, $headerSize);
    $body = substr($response, $headerSize);
    $json = json_decode($body, true);

    return [
        'ok' => true,
        'status' => (int)($info['http_code'] ?? 0),
        'headers' => $rawHeaders,
        'body' => $body,
        'json' => is_array($json) ? $json : null,
        'content_type' => (string)($info['content_type'] ?? ''),
        'url' => (string)($info['url'] ?? $url),
        'time_total' => (float)($info['total_time'] ?? 0),
    ];
}

$baseDir = __DIR__;
$defaultBase = rtrim((string)($_SERVER['REQUEST_SCHEME'] ?? (OTASecurity::isHttps() ? 'https' : 'http')), '/') . '://' . (string)($_SERVER['HTTP_HOST'] ?? 'localhost');
$selfBase = $defaultBase . rtrim(str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME'] ?? '')), '/');

$connectorPing = null;
try {
    $connectorPing = ota_ping_connection();
} catch (Throwable $e) {
    $connectorPing = [
        'success' => false,
        'error' => $e->getMessage(),
    ];
}

$apiMap = [
    'connector_ping' => [
        'label' => 'Connector Ping',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/ping.php',
        'kind' => 'system',
    ],
    'login' => [
        'label' => 'Login',
        'method' => 'POST',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/login.php',
        'payload' => ['username' => 'BOSS', 'password' => '1234'],
        'kind' => 'auth',
    ],
    'dashboard' => [
        'label' => 'Dashboard',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/dashboard.php',
        'kind' => 'dashboard',
    ],
    'users' => [
        'label' => 'Users',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/users.php',
        'kind' => 'collection',
    ],
    'logs' => [
        'label' => 'Logs',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/logs.php',
        'kind' => 'collection',
    ],
    'log_detail' => [
        'label' => 'Log Detail',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/log_detail.php?id=1',
        'kind' => 'detail',
    ],
    'user_detail' => [
        'label' => 'User Detail',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/user_detail.php?id=1',
        'kind' => 'detail',
    ],
    'trace' => [
        'label' => 'Trace',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/trace.php?log_uuid=test',
        'kind' => 'trace',
    ],
    'feed' => [
        'label' => 'Feed',
        'method' => 'GET',
        'url' => '/Assets/Connectors/DeveloperConsoleApi/feed.php',
        'kind' => 'feed',
    ],
];

$runKey = (string)($_GET['run'] ?? '');
$singleResult = null;
$singleKey = null;

if ($runKey !== '' && isset($apiMap[$runKey])) {
    $api = $apiMap[$runKey];
    $fullUrl = preg_match('#^https?://#i', $api['url'])
        ? $api['url']
        : $defaultBase . $api['url'];

    $singleResult = ota_api_request($api['method'], $fullUrl, $api['payload'] ?? null);
    $singleKey = $runKey;
}

$runAll = isset($_GET['run_all']);
$allResults = [];

if ($runAll) {
    foreach ($apiMap as $key => $api) {
        $fullUrl = preg_match('#^https?://#i', $api['url'])
            ? $api['url']
            : $defaultBase . $api['url'];

        $allResults[$key] = ota_api_request($api['method'], $fullUrl, $api['payload'] ?? null);
    }
}

function esc(mixed $value): string
{
    return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');
}

function statusBadge(array $res): string
{
    if (!($res['ok'] ?? false)) {
        return 'error';
    }
    $status = (int)($res['status'] ?? 0);
    if ($status >= 200 && $status < 300) return 'success';
    if ($status >= 400 && $status < 500) return 'warning';
    if ($status >= 500) return 'danger';
    return 'neutral';
}

function renderCard(string $title, array $data): void
{
    $status = statusBadge($data);
    $statusText = $data['ok'] ? ('HTTP ' . (string)($data['status'] ?? 0)) : ('ERR: ' . (string)($data['error'] ?? 'Unknown'));

    echo '<div class="card">';
    echo '<div class="card-top">';
    echo '<div>';
    echo '<div class="card-title">' . esc($title) . '</div>';
    echo '<div class="card-sub">' . esc($statusText) . '</div>';
    echo '</div>';
    echo '<span class="badge badge-' . esc($status) . '">' . esc(strtoupper($status)) . '</span>';
    echo '</div>';

    if (!empty($data['json']) && is_array($data['json'])) {
        echo '<pre class="json">' . esc(json_encode($data['json'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) . '</pre>';
    } else {
        echo '<pre class="json">' . esc((string)($data['body'] ?? $data['error'] ?? 'No body')) . '</pre>';
    }

    echo '</div>';
}

$apiBase = rtrim($defaultBase, '/');
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Developer Console API Tester</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Montserrat:wght@500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root{
      --bg:#0a0b10;
      --panel:#11141b;
      --panel-2:#171b24;
      --text:#eef1f7;
      --muted:#98a2b3;
      --line:rgba(255,255,255,.08);
      --accent:#7c3aed;
      --accent2:#22c55e;
      --warn:#f59e0b;
      --danger:#ef4444;
      --shadow:0 24px 60px rgba(0,0,0,.35);
      --radius:24px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      background:
        radial-gradient(circle at top left, rgba(124,58,237,.18), transparent 28%),
        radial-gradient(circle at top right, rgba(34,197,94,.12), transparent 26%),
        var(--bg);
      color:var(--text);
      font-family:Inter,system-ui,sans-serif;
    }
    .shell{
      max-width:1600px;
      margin:0 auto;
      padding:24px;
    }
    .topbar{
      position:sticky;
      top:0;
      z-index:40;
      backdrop-filter: blur(18px);
      background: rgba(10,11,16,.78);
      border:1px solid var(--line);
      border-radius: 24px;
      padding:18px 22px;
      display:flex;
      gap:16px;
      align-items:center;
      justify-content:space-between;
      box-shadow:var(--shadow);
    }
    .brand{
      display:flex;
      align-items:center;
      gap:14px;
    }
    .logo{
      width:52px;height:52px;border-radius:18px;
      background: linear-gradient(145deg, #7c3aed, #111827);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.1), 0 12px 28px rgba(124,58,237,.28);
      display:grid;place-items:center;
      font-weight:900;
      font-family:Montserrat,sans-serif;
    }
    .brand h1{
      margin:0;
      font-size:1.1rem;
      letter-spacing:-.03em;
      font-weight:900;
    }
    .brand p, .meta{
      margin:3px 0 0;
      color:var(--muted);
      font-size:.84rem;
    }
    .actions{
      display:flex;
      gap:10px;
      flex-wrap:wrap;
      justify-content:flex-end;
    }
    .btn{
      appearance:none;
      border:none;
      cursor:pointer;
      border-radius:14px;
      padding:12px 16px;
      font-weight:800;
      font-family:Montserrat,sans-serif;
      letter-spacing:.02em;
      color:var(--text);
      background:var(--panel-2);
      border:1px solid var(--line);
      text-decoration:none;
      display:inline-flex;
      align-items:center;
      gap:8px;
      box-shadow: 0 10px 26px rgba(0,0,0,.25);
    }
    .btn-primary{ background: linear-gradient(145deg, var(--accent), #4c1d95); }
    .btn-success{ background: linear-gradient(145deg, var(--accent2), #166534); }
    .grid{
      display:grid;
      grid-template-columns: 1.05fr .95fr;
      gap:18px;
      margin-top:18px;
    }
    .panel{
      background:rgba(17,20,27,.92);
      border:1px solid var(--line);
      border-radius:var(--radius);
      box-shadow:var(--shadow);
      overflow:hidden;
    }
    .panel-head{
      padding:18px 20px;
      border-bottom:1px solid var(--line);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:14px;
    }
    .panel-head h2{
      margin:0;
      font-size:1rem;
      font-weight:900;
      letter-spacing:-.03em;
    }
    .panel-head small{ color:var(--muted); }
    .panel-body{ padding:20px; }
    .hero{
      display:grid;
      grid-template-columns: 1.1fr .9fr;
      gap:18px;
    }
    .hero-card{
      background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border:1px solid var(--line);
      border-radius:22px;
      padding:18px;
    }
    .avatar{
      width:76px;height:76px;border-radius:24px;
      object-fit:cover;
      border:1px solid var(--line);
      box-shadow: 0 16px 30px rgba(0,0,0,.3);
    }
    .stat-row{
      display:grid;
      grid-template-columns: repeat(4,1fr);
      gap:12px;
      margin-top:14px;
    }
    .stat{
      padding:14px;
      border-radius:18px;
      background:var(--panel-2);
      border:1px solid var(--line);
    }
    .stat .k{
      color:var(--muted);
      font-size:.72rem;
      text-transform:uppercase;
      letter-spacing:.08em;
      font-weight:800;
    }
    .stat .v{
      font-size:1.3rem;
      font-weight:900;
      margin-top:7px;
    }
    .searchbar{
      display:flex;
      gap:10px;
      align-items:center;
      background:var(--panel-2);
      border:1px solid var(--line);
      border-radius:16px;
      padding:10px 12px;
      margin-top:14px;
    }
    .searchbar input{
      width:100%;
      background:transparent;
      border:none;
      outline:none;
      color:var(--text);
      font-size:.95rem;
    }
    .chips{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
    .chip{
      border:1px solid var(--line);
      background: rgba(255,255,255,.03);
      border-radius:999px;
      padding:8px 12px;
      font-size:.8rem;
      color:var(--text);
    }
    .table{
      width:100%;
      border-collapse:collapse;
      overflow:hidden;
      border-radius:18px;
      border:1px solid var(--line);
    }
    .table th,.table td{
      padding:12px 10px;
      border-bottom:1px solid var(--line);
      text-align:left;
      vertical-align:top;
      font-size:.88rem;
    }
    .table th{
      color:#cbd5e1;
      font-size:.74rem;
      text-transform:uppercase;
      letter-spacing:.08em;
      background: rgba(255,255,255,.03);
    }
    .badge{
      display:inline-flex;
      align-items:center;
      gap:6px;
      padding:6px 10px;
      border-radius:999px;
      font-size:.72rem;
      font-weight:900;
      letter-spacing:.05em;
      text-transform:uppercase;
      border:1px solid var(--line);
    }
    .badge-success{ background:rgba(34,197,94,.16); color:#86efac; }
    .badge-warning{ background:rgba(245,158,11,.16); color:#fcd34d; }
    .badge-danger{ background:rgba(239,68,68,.16); color:#fca5a5; }
    .badge-neutral{ background:rgba(148,163,184,.12); color:#cbd5e1; }
    .badge-error{ background:rgba(239,68,68,.16); color:#fca5a5; }
    .card{
      border:1px solid var(--line);
      border-radius:20px;
      background: rgba(255,255,255,.03);
      padding:16px;
      margin-bottom:14px;
    }
    .card-top{
      display:flex;
      justify-content:space-between;
      gap:10px;
      align-items:flex-start;
      margin-bottom:10px;
    }
    .card-title{ font-weight:900; font-size:.98rem; }
    .card-sub{ color:var(--muted); font-size:.8rem; margin-top:4px; }
    .json{
      margin:0;
      white-space:pre-wrap;
      word-break:break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size:.78rem;
      line-height:1.55;
      color:#e2e8f0;
      background: rgba(0,0,0,.24);
      border:1px solid var(--line);
      padding:14px;
      border-radius:16px;
      max-height:560px;
      overflow:auto;
    }
    .scroll{
      max-height:760px;
      overflow:auto;
      padding-right:4px;
    }
    .subgrid{
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:14px;
    }
    .mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .muted{ color:var(--muted); }
    .section-title{
      margin:0 0 10px;
      font-size:.95rem;
      font-weight:900;
      letter-spacing:-.02em;
    }
    .list{
      display:flex;
      flex-direction:column;
      gap:10px;
    }
    .item{
      padding:14px;
      border-radius:18px;
      border:1px solid var(--line);
      background: rgba(255,255,255,.02);
    }
    .item-top{
      display:flex;
      justify-content:space-between;
      gap:10px;
      align-items:center;
      margin-bottom:8px;
    }
    .item-title{ font-weight:900; }
    .item-meta{ color:var(--muted); font-size:.8rem; }
    .footer-note{
      margin-top:16px;
      color:var(--muted);
      font-size:.82rem;
      line-height:1.6;
    }
    .responsive{
      overflow:auto;
    }
    @media (max-width: 1180px){
      .grid,.hero,.subgrid{ grid-template-columns:1fr; }
      .stat-row{ grid-template-columns: repeat(2,1fr); }
    }
    @media (max-width: 760px){
      .shell{ padding:14px; }
      .topbar{ padding:14px; border-radius:20px; }
      .actions{ width:100%; justify-content:flex-start; }
      .stat-row{ grid-template-columns:1fr 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="topbar">
      <div class="brand">
        <div class="logo">OA</div>
        <div>
          <h1>Developer Console API Tester</h1>
          <p>OnTrackAssets · secure diagnostics panel</p>
        </div>
      </div>
      <div class="actions">
        <a class="btn btn-primary" href="?run_all=1">Run All APIs</a>
        <a class="btn" href="?">Reset</a>
        <a class="btn btn-success" href="<?= esc($apiBase) ?>" target="_blank" rel="noopener">Open Host</a>
      </div>
    </div>

    <div class="grid">
      <div class="panel">
        <div class="panel-head">
          <div>
            <h2>Overview</h2>
            <small>Login, users, logs, trace, detail views and connector health.</small>
          </div>
          <span class="badge badge-neutral">PHP</span>
        </div>
        <div class="panel-body">
          <div class="hero">
            <div class="hero-card">
              <div style="display:flex;align-items:center;gap:16px;">
                <img class="avatar" src="https://avatars.githubusercontent.com/u/72921622?v=4" alt="Developer avatar">
                <div>
                  <div style="font-size:1.2rem;font-weight:900;letter-spacing:-.03em;">BOSS294</div>
                  <div class="muted" style="margin-top:4px;">Mayank Chawdhari · Developer</div>
                  <div class="muted" style="margin-top:4px;">Company: On Track Assesment</div>
                  <div class="muted" style="margin-top:4px;">Role: Developer</div>
                </div>
              </div>

              <div class="chips">
                <span class="chip">BOSS / 1234 login</span>
                <span class="chip">Users feed</span>
                <span class="chip">System logs</span>
                <span class="chip">Trace lookup</span>
                <span class="chip">Tablet-ready console</span>
              </div>

              <div class="searchbar">
                <span class="mono muted">/</span>
                <input id="apiSearch" type="text" placeholder="Filter APIs, logs, users, trace..." oninput="filterCards(this.value)">
              </div>

              <div class="footer-note">
                This page calls the developer-only API bundle from the same directory and keeps the output readable for high-volume log inspection.
              </div>
            </div>

            <div class="hero-card">
              <div class="section-title">Connector status</div>
              <table class="table">
                <tr><th>Item</th><th>Value</th></tr>
                <tr><td>Connector version</td><td><?= esc($connectorPing['version'] ?? OTA_CONNECTOR_VERSION) ?></td></tr>
                <tr><td>Ping</td><td>
                  <?php if (($connectorPing['success'] ?? false) && !empty($connectorPing['result']['alive'])): ?>
                    <span class="badge badge-success">Alive</span>
                  <?php else: ?>
                    <span class="badge badge-danger">Down</span>
                  <?php endif; ?>
                </td></tr>
                <tr><td>Latency</td><td><?= esc((string)($connectorPing['result']['latency_ms'] ?? 'n/a')) ?> ms</td></tr>
                <tr><td>DB driver</td><td><?= esc((string)($connectorPing['result']['driver'] ?? 'n/a')) ?></td></tr>
              </table>
            </div>
          </div>

          <div class="stat-row">
            <div class="stat"><div class="k">API Count</div><div class="v"><?= count($apiMap) ?></div></div>
            <div class="stat"><div class="k">Users</div><div class="v">Live</div></div>
            <div class="stat"><div class="k">Logs</div><div class="v">Live</div></div>
            <div class="stat"><div class="k">Mode</div><div class="v">Dev</div></div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div>
            <h2>API Buttons</h2>
            <small>Tap to test each endpoint individually.</small>
          </div>
          <span class="badge badge-neutral">Actions</span>
        </div>
        <div class="panel-body">
          <div class="list">
            <?php foreach ($apiMap as $key => $api): ?>
              <div class="item">
                <div class="item-top">
                  <div>
                    <div class="item-title"><?= esc($api['label']) ?></div>
                    <div class="item-meta"><?= esc($api['method']) ?> · <?= esc($api['url']) ?></div>
                  </div>
                  <a class="btn" href="?run=<?= esc($key) ?>">Run</a>
                </div>
              </div>
            <?php endforeach; ?>
          </div>
          <div class="footer-note">
            For fixed endpoints like log detail or user detail, change the ID query string directly in the file.
          </div>
        </div>
      </div>
    </div>

    <div class="grid" style="margin-top:18px;">
      <div class="panel">
        <div class="panel-head">
          <div>
            <h2>Responses</h2>
            <small>Raw JSON and formatted view.</small>
          </div>
          <span class="badge badge-neutral">Results</span>
        </div>
        <div class="panel-body">
          <?php if ($singleResult !== null && $singleKey !== null): ?>
            <?php renderCard($apiMap[$singleKey]['label'], $singleResult); ?>
          <?php endif; ?>

          <?php if ($runAll): ?>
            <div class="subgrid">
              <?php foreach ($allResults as $key => $res): ?>
                <?php renderCard($apiMap[$key]['label'], $res); ?>
              <?php endforeach; ?>
            </div>
          <?php endif; ?>

          <?php if ($singleResult === null && !$runAll): ?>
            <div class="card">
              <div class="card-title">No API executed yet</div>
              <div class="card-sub">Use the buttons above or “Run All APIs”.</div>
            </div>
          <?php endif; ?>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div>
            <h2>Detected Data</h2>
            <small>Users and logs summary placeholders for live payloads.</small>
          </div>
          <span class="badge badge-neutral">Inspect</span>
        </div>
        <div class="panel-body">
          <div class="responsive">
            <div class="section-title">Recent users</div>
            <div class="list">
              <div class="item">
                <div class="item-title">Loaded from users endpoint</div>
                <div class="item-meta">When your endpoint returns `data.users`, render them here as cards.</div>
              </div>
              <div class="item">
                <div class="item-title">User detail button</div>
                <div class="item-meta">Show full user profile, status, role, last login and contact info.</div>
              </div>
            </div>

            <div style="height:14px;"></div>

            <div class="section-title">Recent logs</div>
            <div class="list">
              <div class="item">
                <div class="item-title">Different colors by type</div>
                <div class="item-meta">info / success / warning / blocked / error / critical</div>
              </div>
              <div class="item">
                <div class="item-title">Trace button</div>
                <div class="item-meta">Query previous logs by user, session, IP, fingerprint or log UUID.</div>
              </div>
              <div class="item">
                <div class="item-title">Mass logs handling</div>
                <div class="item-meta">Paginate, group by type, and collapse details before rendering many rows.</div>
              </div>
            </div>
          </div>

          <div class="footer-note">
            This page is intentionally plain PHP so it can be dropped into the same folder as the developer console API and used immediately for endpoint validation.
          </div>
        </div>
      </div>
    </div>

    <div class="panel" style="margin-top:18px;">
      <div class="panel-head">
        <div>
          <h2>How to wire the live endpoints</h2>
          <small>Edit the `$apiMap` URLs if your filenames differ.</small>
        </div>
      </div>
      <div class="panel-body">
        <pre class="json"><?=
esc(<<<TXT
1. Place this file beside connector.php and DeveloperConsoleApi/
2. Update each API path in \$apiMap if your filenames differ
3. Open dev_api_tester.php in the browser
4. Click Run on each endpoint or Run All APIs
5. Use the JSON output for debugging and development

Recommended endpoints:
- /Assets/Connectors/DeveloperConsoleApi/ping.php
- /Assets/Connectors/DeveloperConsoleApi/login.php
- /Assets/Connectors/DeveloperConsoleApi/dashboard.php
- /Assets/Connectors/DeveloperConsoleApi/users.php
- /Assets/Connectors/DeveloperConsoleApi/logs.php
- /Assets/Connectors/DeveloperConsoleApi/log_detail.php?id=1
- /Assets/Connectors/DeveloperConsoleApi/user_detail.php?id=1
- /Assets/Connectors/DeveloperConsoleApi/trace.php?log_uuid=test
- /Assets/Connectors/DeveloperConsoleApi/feed.php
TXT)
?></pre>
      </div>
    </div>
  </div>

  <script>
    function filterCards(q) {
      q = (q || '').toLowerCase().trim();
      document.querySelectorAll('.item, .card, .stat, .hero-card').forEach((el) => {
        const txt = (el.innerText || el.textContent || '').toLowerCase();
        el.style.display = txt.includes(q) ? '' : 'none';
      });
    }
  </script>
</body>
</html>