<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class Jwt
{
    private static function secret(?string $secret): string
    {
        $secret ??= trim((string) OTAEnv::get('JWT_SECRET', 'saidhgusyadbuisadbusahfuydsffg7y8dhuyshdfiudsgfdsjf8dshfugydsbfuidsbfuyhdugf'));

        if ($secret === '') {
            throw new RuntimeException('JWT_SECRET is not configured.');
        }

        return $secret;
    }

    public static function encode(array $payload, ?string $secret = null): string
    {
        $secret = self::secret($secret);

        $header = [
            'alg' => 'HS256',
            'typ' => 'JWT',
        ];

        $header64 = self::base64UrlEncode(
            json_encode($header, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR)
        );

        $payload64 = self::base64UrlEncode(
            json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR)
        );

        $signingInput = $header64 . '.' . $payload64;

        $signature = hash_hmac(
            'sha256',
            $signingInput,
            $secret,
            true
        );

        return $signingInput . '.' . self::base64UrlEncode($signature);
    }

    public static function decode(string $jwt, ?string $secret = null): array
    {
        $secret = self::secret($secret);

        $parts = explode('.', $jwt);

        if (count($parts) !== 3) {
            throw new RuntimeException('Invalid JWT format.');
        }

        [$header64, $payload64, $signature64] = $parts;

        $expected = self::base64UrlEncode(
            hash_hmac(
                'sha256',
                $header64 . '.' . $payload64,
                $secret,
                true
            )
        );

        if (!hash_equals($expected, $signature64)) {
            throw new RuntimeException('JWT signature mismatch.');
        }

        $payload = json_decode(
            self::base64UrlDecode($payload64),
            true,
            512,
            JSON_THROW_ON_ERROR
        );

        if (!is_array($payload)) {
            throw new RuntimeException('Invalid JWT payload.');
        }

        $now = time();

        if (isset($payload['nbf']) && $now < (int)$payload['nbf']) {
            throw new RuntimeException('JWT not active yet.');
        }

        if (isset($payload['iat']) && (int)$payload['iat'] > ($now + 60)) {
            throw new RuntimeException('JWT issued in the future.');
        }

        if (isset($payload['exp']) && $now >= (int)$payload['exp']) {
            throw new RuntimeException('JWT expired.');
        }

        return $payload;
    }

    private static function base64UrlEncode(string $data): string
    {
        return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
    }

    private static function base64UrlDecode(string $data): string
    {
        $remainder = strlen($data) % 4;

        if ($remainder !== 0) {
            $data .= str_repeat('=', 4 - $remainder);
        }

        $decoded = base64_decode(
            strtr($data, '-_', '+/'),
            true
        );

        if ($decoded === false) {
            throw new RuntimeException('Invalid Base64URL encoding.');
        }

        return $decoded;
    }
}