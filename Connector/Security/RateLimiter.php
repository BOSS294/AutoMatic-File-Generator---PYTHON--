<?php
declare(strict_types=1);

/**
 * NileAndSinai V2 - File Rate Limiter
 * Version: 4.0.0
 *
 * Atomic, lock-protected filesystem limiter.
 *
 * Storage order:
 *   1. RATE_LIMIT_DIR
 *   2. A private directory one level above DOCUMENT_ROOT
 *   3. A project-local Runtime directory
 *   4. PHP system temp directory
 *
 * Never expose the limiter state directory publicly.
 */
final class RateLimiter
{
    public static function hit(
        string $key,
        int $limit = 60,
        int $windowSeconds = 60
    ): array {
        $key = trim($key);

        if ($key === '') {
            throw new InvalidArgumentException('Rate-limit key cannot be empty.');
        }

        if ($limit < 1 || $windowSeconds < 1) {
            throw new InvalidArgumentException(
                'Rate-limit limit and window must be greater than zero.'
            );
        }

        $directory = self::resolveStorageDirectory();

        $file = $directory
            . DIRECTORY_SEPARATOR
            . hash('sha256', $key)
            . '.json';

        $handle = @fopen($file, 'c+');

        if ($handle === false) {
            throw new RuntimeException(
                'Unable to open rate limiter state.'
            );
        }

        try {
            if (!flock($handle, LOCK_EX)) {
                throw new RuntimeException(
                    'Unable to lock rate limiter state.'
                );
            }

            rewind($handle);

            $raw = stream_get_contents($handle);

            $data = is_string($raw) && trim($raw) !== ''
                ? json_decode($raw, true)
                : null;

            $now = time();

            if (
                !is_array($data)
                || !isset($data['start'], $data['count'])
                || ($now - (int) $data['start']) >= $windowSeconds
            ) {
                $data = [
                    'start' => $now,
                    'count' => 0,
                ];
            }

            $data['count'] = (int) $data['count'] + 1;

            $payload = json_encode(
                $data,
                JSON_UNESCAPED_SLASHES
                | JSON_UNESCAPED_UNICODE
                | JSON_THROW_ON_ERROR
            );

            rewind($handle);
            ftruncate($handle, 0);

            if (fwrite($handle, $payload) === false) {
                throw new RuntimeException(
                    'Unable to persist rate limiter state.'
                );
            }

            fflush($handle);
            flock($handle, LOCK_UN);

            $count = (int) $data['count'];

            return [
                'allowed' => $count <= $limit,
                'count' => $count,
                'limit' => $limit,
                'windowSeconds' => $windowSeconds,
                'remaining' => max(0, $limit - $count),
                'retry_after' => max(
                    0,
                    $windowSeconds - ($now - (int) $data['start'])
                ),
            ];
        } finally {
            fclose($handle);
        }
    }

    private static function resolveStorageDirectory(): string
    {
        $candidates = [];

        $configured = getenv('RATE_LIMIT_DIR');

        if (is_string($configured) && trim($configured) !== '') {
            $candidates[] = rtrim(trim($configured), '/\\');
        }

        $documentRoot = (string) ($_SERVER['DOCUMENT_ROOT'] ?? '');

        if ($documentRoot !== '') {
            $candidates[] = dirname(rtrim($documentRoot, '/\\'))
                . DIRECTORY_SEPARATOR
                . 'nileandsinai_runtime'
                . DIRECTORY_SEPARATOR
                . 'rate_limiter';
        }

        $candidates[] = dirname(__DIR__, 2)
            . DIRECTORY_SEPARATOR
            . 'Runtime'
            . DIRECTORY_SEPARATOR
            . 'rate_limiter';

        $candidates[] = sys_get_temp_dir()
            . DIRECTORY_SEPARATOR
            . 'nileandsinai_rate_limiter';

        foreach (array_unique($candidates) as $candidate) {
            if ($candidate === '') {
                continue;
            }

            if (!is_dir($candidate)) {
                @mkdir($candidate, 0700, true);
            }

            if (is_dir($candidate) && is_writable($candidate)) {
                @chmod($candidate, 0700);
                return $candidate;
            }
        }

        throw new RuntimeException(
            'Unable to initialize rate limiter storage.'
        );
    }
}
