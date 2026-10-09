<?php
declare(strict_types=1);

/**
 * NEXUS V1 — Central permission map.
 *
 * Versioned delivery file; deploy as Permissions.php.
 */
final class Permissions
{
    private const MAP = [
        'boss' => [
            'all',
        ],
        'admin' => [
            'all',
        ],
        'manager' => [
            'view_dashboard',

            'view_catalogue',
            'manage_catalogue',
            'manage_products',
            'manage_collections',
            'manage_variations',
            'manage_reviews',

            'view_billing',
            'manage_billing',

            'view_customer_sales',
            'manage_enquiries',
            'manage_quotes',
            'manage_custom_jewellery',
            'manage_contact_messages',

            'view_content',
            'manage_content',
            'manage_pages',
            'manage_faqs',
            'manage_media',

            'view_seo',
            'manage_seo',

            'view_configuration',
            'manage_configuration',

            'view_panel_updates',
            'manage_panel_updates',

            'view_logs',

            'manage_assessment',
            'manage_users',
        ],
        'candidate' => [
            'start_assessment',
            'submit_answer',
            'view_assessment',
        ],
        'guest' => [
            'view_public',
        ],
    ];

    public static function all(): array
    {
        return self::MAP;
    }

    public static function roles(): array
    {
        return array_keys(self::MAP);
    }

    public static function permissionsFor(string $role): array
    {
        $role = self::normalizeRole($role);

        return self::MAP[$role] ?? [];
    }

    public static function can(string $role, string $permission): bool
    {
        $permission = trim($permission);

        if ($permission === '') {
            return false;
        }

        $permissions = self::permissionsFor($role);

        return in_array('all', $permissions, true)
            || in_array($permission, $permissions, true);
    }

    public static function canAny(string $role, array $permissions): bool
    {
        foreach ($permissions as $permission) {
            if (is_string($permission) && self::can($role, $permission)) {
                return true;
            }
        }

        return false;
    }

    public static function canAll(string $role, array $permissions): bool
    {
        $checked = 0;

        foreach ($permissions as $permission) {
            if (!is_string($permission)) {
                continue;
            }

            $checked++;

            if (!self::can($role, $permission)) {
                return false;
            }
        }

        return $checked > 0;
    }

    public static function catalog(): array
    {
        $catalog = [];

        foreach (self::MAP as $permissions) {
            foreach ($permissions as $permission) {
                if ($permission === 'all') {
                    continue;
                }

                $catalog[$permission] = true;
            }
        }

        $permissions = array_keys($catalog);
        sort($permissions, SORT_STRING);

        return $permissions;
    }

    private static function normalizeRole(string $role): string
    {
        return strtolower(trim($role));
    }
}
