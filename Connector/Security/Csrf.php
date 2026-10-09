<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/Auth/Session.php';

/**
 * NileAndSinai V2 - CSRF Protection
 * Version: 1.0.0
 *
 * Use for state-changing, session-authenticated browser requests.
 */

final class Csrf
{
    private const SESSION_KEY = '_nsa_csrf_token';
    private const TOKEN_BYTES = 32;

    public static function token(): string
    {
        $existing = Session::get(self::SESSION_KEY);

        if (is_string($existing) && strlen($existing) >= 32) {
            return $existing;
        }

        $token = bin2hex(random_bytes(self::TOKEN_BYTES));
        Session::set(self::SESSION_KEY, $token);

        return $token;
    }

    public static function validate(?string $token): bool
    {
        $token = trim((string) $token);
        $stored = Session::get(self::SESSION_KEY);

        if (!is_string($stored) || $stored === '' || $token === '') {
            return false;
        }

        return hash_equals($stored, $token);
    }

    public static function assertValid(?string $token = null): void
    {
        $token ??= (string) (
            $_SERVER['HTTP_X_CSRF_TOKEN']
            ?? $_POST['_csrf']
            ?? ''
        );

        if (!self::validate($token)) {
            throw new RuntimeException('Invalid CSRF token.', 403);
        }
    }

    public static function rotate(): string
    {
        $token = bin2hex(random_bytes(self::TOKEN_BYTES));
        Session::set(self::SESSION_KEY, $token);
        return $token;
    }
}