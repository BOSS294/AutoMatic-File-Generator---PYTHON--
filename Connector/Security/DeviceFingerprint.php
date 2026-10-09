<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

/**
 * NileAndSinai V2 - Risk Fingerprint
 * Version: 2.0.0
 *
 * This is a risk/correlation signal, not a cryptographic device identity.
 */

final class DeviceFingerprint
{
    public static function generate(): string
    {
        $parts = [
            OTASecurity::clientIp(),
            (string) ($_SERVER['HTTP_USER_AGENT'] ?? ''),
            (string) ($_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? ''),
            (string) ($_SERVER['HTTP_ACCEPT_ENCODING'] ?? ''),
            (string) ($_SERVER['HTTP_ORIGIN'] ?? ''),
        ];

        return hash('sha256', implode('|', $parts));
    }

    public static function riskSignal(): string
    {
        return self::generate();
    }
}