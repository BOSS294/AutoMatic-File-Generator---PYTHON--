<?php

declare(strict_types=1);

/**
 * ============================================================================
 * NileAndSinai V2 - Security Facade
 * ============================================================================
 *
 * File       : Security.php
 * Version    : 2.0.0
 *
 * PURPOSE
 * -------
 * Provides the public security facade consumed by _bootstrap.php and APIs.
 *
 * Responsibilities:
 *   - Security headers
 *   - Content Security Policy
 *   - HTTPS enforcement
 *   - Trusted-origin validation
 *   - HTTP method validation
 *   - Client IP resolution
 *
 * The actual low-level security implementation remains inside OTASecurity.
 * This class provides the stable Connector-facing API.
 *
 * Created by:
 *   Mayank Chawdhari aka BOSS294
 *   Privonix Technologies
 *
 * Copyright © 2026 Mayank Chawdhari / Privonix Technologies.
 * ============================================================================
 */

require_once dirname(__DIR__) . '/connector.php';

final class Security
{
    /**
     * Initialize the Connector security layer.
     *
     * @param bool $csp
     * @param string|null $cspNonce
     */
    public static function init(
        bool $csp = true,
        ?string $cspNonce = null
    ): void {
        OTASecurity::applyHeaders();

        if ($csp) {
            self::applyContentSecurityPolicy($cspNonce);
        }

        OTASecurity::assertHttpsOrThrow();
        OTASecurity::assertOriginOrThrow();
    }

    /**
     * Apply the Content Security Policy.
     *
     * The nonce is only included when supplied.
     * This allows normal APIs to use a strict baseline CSP while
     * pages requiring inline scripts can receive a per-request nonce.
     */
    private static function applyContentSecurityPolicy(
        ?string $nonce = null
    ): void {
        if (PHP_SAPI === 'cli' || headers_sent()) {
            return;
        }

        $scriptSrc = "'self' https://unpkg.com";
        if ($nonce !== null && $nonce !== '') {
            $scriptSrc .= " 'nonce-" . $nonce . "'";
        }

        $connectSrc = trim(
            (string) OTAEnv::get('CSP_CONNECT_SRC', "'self'")
        );

        if ($connectSrc === '') {
            $connectSrc = "'self'";
        }

        if ($connectSrc === 'self') {
            $connectSrc = "'self'";
        }

        $policy = implode('; ', [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "script-src {$scriptSrc}",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self' data:",
            "connect-src {$connectSrc}",
            "media-src 'self' blob:",
            "worker-src 'self' blob:",
        ]);

        header(
            'Content-Security-Policy: ' . $policy
        );
    }

    /**
     * Validate the current HTTP method.
     */
    public static function validate(
        array $allowedMethods = ['GET', 'POST']
    ): void {
        OTASecurity::assertRequestMethod($allowedMethods);
    }

    /**
     * Return the resolved client IP.
     */
    public static function clientIp(): string
    {
        return OTASecurity::clientIp();
    }
}