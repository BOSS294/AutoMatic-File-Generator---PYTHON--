<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class Token
{
    public static function generate(int $bytes = 32): string
    {
        return bin2hex(random_bytes($bytes));
    }

    public static function hash(string $value): string
    {
        $secret = (string) OTAEnv::get('TOKEN_SECRET', (string) OTAEnv::get('JWT_SECRET', 'ota_secret'));
        return hash_hmac('sha256', $value, $secret);
    }

    public static function verify(string $value, string $hash): bool
    {
        return hash_equals(self::hash($value), $hash);
    }
}
