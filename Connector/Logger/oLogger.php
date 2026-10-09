<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';
require_once dirname(__DIR__) . '/Database/Database.php';
require_once __DIR__ . '/LogTypes.php';

/**
 * NileAndSinai V2 - Structured Logger
 * Version: 2.0.0
 *
 * Logging is best-effort: a logging failure must never replace the primary
 * application response.
 */

final class OTALogger
{
    public static function log(
        string $type,
        string $status,
        string $message,
        array $details = [],
        ?PDO $pdo = null,
        string $source = LogTypes::SOURCE_PHP,
        ?string $niceMessage = null,
        ?int $userId = null,
        ?string $sessionId = null,
        ?string $path = null,
        ?int $responseStatus = null
    ): bool {
        try {
            $pdo ??= ota_db();

            $details = self::enrichDetails($details);
            $niceMessage ??= self::makeNiceMessage($type, $status, $message);

            $sql = "
                INSERT INTO system_logs
                (
                    log_uuid, log_type, source, status, nice_message, message,
                    details_json, user_id, session_id, request_method, request_path,
                    request_origin, request_ip, user_agent, device_fingerprint
                )
                VALUES
                (
                    :log_uuid, :log_type, :source, :status, :nice_message, :message,
                    :details_json, :user_id, :session_id, :request_method, :request_path,
                    :request_origin, :request_ip, :user_agent, :device_fingerprint
                )
            ";

            $stmt = $pdo->prepare($sql);

            return $stmt->execute([
                ':log_uuid' => self::uuid(),
                ':log_type' => $type,
                ':source' => $source,
                ':status' => $status,
                ':nice_message' => $niceMessage,
                ':message' => $message,
                ':details_json' => json_encode(
                    $details,
                    JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE
                ),
                ':user_id' => $userId,
                ':session_id' => $sessionId,
                ':request_method' => strtoupper((string) ($_SERVER['REQUEST_METHOD'] ?? 'CLI')),
                ':request_path' => $path ?? (string) ($_SERVER['REQUEST_URI'] ?? ''),
                ':request_origin' => (string) ($_SERVER['HTTP_ORIGIN'] ?? ''),
                ':request_ip' => OTASecurity::clientIp(),
                ':user_agent' => substr(
                    (string) ($_SERVER['HTTP_USER_AGENT'] ?? 'CLI'),
                    0,
                    512
                ),
                ':device_fingerprint' => class_exists('DeviceFingerprint')
                    ? DeviceFingerprint::generate()
                    : null,
            ]);
        } catch (Throwable $e) {
            /*
             * Logging must never crash the actual API.
             * Optionally mirror the failure to PHP's error log.
             */
            error_log(
                '[NileAndSinai Logger Failure] '
                . $e->getMessage()
            );

            return false;
        }
    }

    public static function logBlocker(
        string $blockerType,
        string $reason,
        array $details = [],
        ?PDO $pdo = null,
        ?int $userId = null,
        ?string $sessionId = null,
        ?string $niceMessage = null
    ): bool {
        try {
            $pdo ??= ota_db();

            $details = self::enrichDetails($details);
            $niceMessage ??= self::makeNiceMessage(
                'blocker',
                LogTypes::BLOCKED,
                $reason
            );

            $sql = "
                INSERT INTO blocker_logs
                (
                    log_uuid, session_id, user_id, blocker_type, blocker_reason,
                    nice_message, message, details_json, is_fullscreen,
                    fullscreen_gap_seconds, tab_switch_count, devtools_count,
                    visibility_count, keyboard_count, contextmenu_count,
                    request_ip, user_agent
                )
                VALUES
                (
                    :log_uuid, :session_id, :user_id, :blocker_type,
                    :blocker_reason, :nice_message, :message, :details_json,
                    :is_fullscreen, :fullscreen_gap_seconds, :tab_switch_count,
                    :devtools_count, :visibility_count, :keyboard_count,
                    :contextmenu_count, :request_ip, :user_agent
                )
            ";

            $stmt = $pdo->prepare($sql);

            return $stmt->execute([
                ':log_uuid' => self::uuid(),
                ':session_id' => $sessionId,
                ':user_id' => $userId,
                ':blocker_type' => $blockerType,
                ':blocker_reason' => $reason,
                ':nice_message' => $niceMessage,
                ':message' => $details['message'] ?? $reason,
                ':details_json' => json_encode(
                    $details,
                    JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE
                ),
                ':is_fullscreen' => (int) ($details['is_fullscreen'] ?? 0),
                ':fullscreen_gap_seconds' => (int) ($details['fullscreen_gap_seconds'] ?? 0),
                ':tab_switch_count' => (int) ($details['tab_switch_count'] ?? 0),
                ':devtools_count' => (int) ($details['devtools_count'] ?? 0),
                ':visibility_count' => (int) ($details['visibility_count'] ?? 0),
                ':keyboard_count' => (int) ($details['keyboard_count'] ?? 0),
                ':contextmenu_count' => (int) ($details['contextmenu_count'] ?? 0),
                ':request_ip' => OTASecurity::clientIp(),
                ':user_agent' => substr(
                    (string) ($_SERVER['HTTP_USER_AGENT'] ?? 'CLI'),
                    0,
                    512
                ),
            ]);
        } catch (Throwable $e) {
            error_log(
                '[NileAndSinai Blocker Logger Failure] '
                . $e->getMessage()
            );

            return false;
        }
    }

    public static function info(
        string $message,
        array $details = [],
        ?PDO $pdo = null,
        ?int $userId = null,
        ?string $sessionId = null
    ): bool {
        return self::log(
            LogTypes::INFO,
            LogTypes::INFO,
            $message,
            $details,
            $pdo,
            LogTypes::SOURCE_PHP,
            null,
            $userId,
            $sessionId
        );
    }

    public static function warning(
        string $message,
        array $details = [],
        ?PDO $pdo = null,
        ?int $userId = null,
        ?string $sessionId = null
    ): bool {
        return self::log(
            LogTypes::WARNING,
            LogTypes::WARNING,
            $message,
            $details,
            $pdo,
            LogTypes::SOURCE_PHP,
            null,
            $userId,
            $sessionId
        );
    }

    public static function error(
        string $message,
        array $details = [],
        ?PDO $pdo = null,
        ?int $userId = null,
        ?string $sessionId = null
    ): bool {
        return self::log(
            LogTypes::ERROR,
            LogTypes::ERROR,
            $message,
            $details,
            $pdo,
            LogTypes::SOURCE_PHP,
            null,
            $userId,
            $sessionId
        );
    }

    public static function security(
        string $message,
        array $details = [],
        ?PDO $pdo = null,
        ?int $userId = null,
        ?string $sessionId = null
    ): bool {
        return self::log(
            LogTypes::BLOCKED,
            LogTypes::BLOCKED,
            $message,
            $details,
            $pdo,
            LogTypes::SOURCE_SYSTEM,
            null,
            $userId,
            $sessionId
        );
    }

    public static function assessment(
        string $message,
        array $details = [],
        ?PDO $pdo = null,
        ?int $userId = null,
        ?string $sessionId = null
    ): bool {
        return self::log(
            'assessment',
            LogTypes::SUCCESS,
            $message,
            $details,
            $pdo,
            LogTypes::SOURCE_API,
            null,
            $userId,
            $sessionId
        );
    }

    public static function makeNiceMessage(
        string $type,
        string $status,
        string $message
    ): string {
        $type = ucfirst(str_replace(['_', '-'], ' ', $type));
        $status = ucfirst(str_replace(['_', '-'], ' ', $status));

        return trim("{$type} | {$status}: {$message}");
    }

    private static function enrichDetails(array $details): array
    {
        $details['_request_id'] = class_exists('RequestContext')
            ? RequestContext::id()
            : null;

        $details['_path'] = (string) ($_SERVER['REQUEST_URI'] ?? '');
        $details['_method'] = strtoupper(
            (string) ($_SERVER['REQUEST_METHOD'] ?? 'CLI')
        );

        if (class_exists('RequestContext')) {
            $details['_execution_ms'] = RequestContext::elapsedMs();
        }

        return $details;
    }

    private static function uuid(): string
    {
        $data = random_bytes(16);
        $data[6] = chr((ord($data[6]) & 0x0f) | 0x40);
        $data[8] = chr((ord($data[8]) & 0x3f) | 0x80);

        return vsprintf(
            '%s%s-%s-%s-%s-%s%s%s',
            str_split(bin2hex($data), 4)
        );
    }
}

function ota_log_event(
    string $type,
    string $status,
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    string $source = LogTypes::SOURCE_PHP,
    ?string $niceMessage = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::log(
        $type,
        $status,
        $message,
        $details,
        $pdo,
        $source,
        $niceMessage,
        $userId,
        $sessionId
    );
}

function ota_log_blocker(
    string $blockerType,
    string $reason,
    array $details = [],
    ?PDO $pdo = null,
    ?int $userId = null,
    ?string $sessionId = null,
    ?string $niceMessage = null
): bool {
    return OTALogger::logBlocker(
        $blockerType,
        $reason,
        $details,
        $pdo,
        $userId,
        $sessionId,
        $niceMessage
    );
}

function log_info(
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::info($message, $details, $pdo, $userId, $sessionId);
}

function log_warning(
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::warning($message, $details, $pdo, $userId, $sessionId);
}

function log_error(
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::error($message, $details, $pdo, $userId, $sessionId);
}

function log_security(
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::security($message, $details, $pdo, $userId, $sessionId);
}

function log_assessment(
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::assessment($message, $details, $pdo, $userId, $sessionId);
}