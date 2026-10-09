<?php
declare(strict_types=1);

/**
 * NileAndSinai V2 - Central API Exception Handler
 * Version: 1.0.0
 */

final class ApiExceptionHandler
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }

        set_exception_handler(static function (Throwable $e): void {
            self::handle($e);
        });

        self::$registered = true;
    }

    public static function handle(Throwable $e): never
    {
        $status = self::statusCode($e);
        $debug = self::debugEnabled();

        $requestId = class_exists('RequestContext')
            ? RequestContext::id()
            : null;

        if (class_exists('OTALogger')) {
            OTALogger::error(
                'Unhandled API exception',
                [
                    'exception' => get_class($e),
                    'code' => $e->getCode(),
                    'request_id' => $requestId,
                    'error' => $debug ? $e->getMessage() : 'redacted',
                    'file' => $debug ? $e->getFile() : null,
                    'line' => $debug ? $e->getLine() : null,
                ],
                null,
                null,
                null
            );
        }

        $message = $status >= 500 && !$debug
            ? 'Internal server error.'
            : $e->getMessage();

        $data = [
            'request_id' => $requestId,
        ];

        if ($e instanceof ValidationException) {
            $data['errors'] = $e->errors();
        }

        if ($e instanceof RateLimitException) {
            $data['rate_limit'] = $e->meta();
        }

        Response::error($message, $status, $data);
    }

    private static function statusCode(Throwable $e): int
    {
        if ($e instanceof ValidationException) {
            return 422;
        }

        if ($e instanceof AuthenticationException) {
            return 401;
        }

        if ($e instanceof AuthorizationException || $e instanceof SecurityException) {
            return 403;
        }

        if ($e instanceof RateLimitException) {
            return 429;
        }

        $code = (int) $e->getCode();

        return ($code >= 400 && $code <= 599) ? $code : 500;
    }

    private static function debugEnabled(): bool
    {
        $env = strtolower((string) OTAEnv::get('APP_ENV', 'production'));
        return in_array($env, ['local', 'development', 'dev', 'testing'], true);
    }
}