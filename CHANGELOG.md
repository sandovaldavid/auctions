# Changelog

## [0.2.3-beta.0](https://github.com/sandovaldavid/auctions/compare/v0.2.2-beta.0...v0.2.3-beta.0) (2026-07-02)


### Documentation

* **docs:** add full project audit and rewrite docker guide ([#57](https://github.com/sandovaldavid/auctions/issues/57)) ([896fb27](https://github.com/sandovaldavid/auctions/commit/896fb2730a45d51d2f9e136e06096040702ab541))

## [0.2.2-beta.0](https://github.com/sandovaldavid/auctions/compare/v0.2.1-beta.0...v0.2.2-beta.0) (2026-06-20)


### Documentation

* **docs:** document merge vs squash strategy for main→develop backsyncs ([b078e44](https://github.com/sandovaldavid/auctions/commit/b078e44d673037c972e4100806251cebcf4096e2))
* **docs:** update merge strategy — develop→main uses merge commit not squash ([c9cda73](https://github.com/sandovaldavid/auctions/commit/c9cda73fd583e2f3cb9c4f428794044e5708dd25))

## [0.2.0](https://github.com/sandovaldavid/auctions/compare/v0.1.1...v0.2.0) (2026-06-20)


### Features

* add data management script for auction project ([892298b](https://github.com/sandovaldavid/auctions/commit/892298b4a55a03d03f854793aba75a87d49f8c31))
* add frontend javascript modules for alerts, dashboard and search ([4f3db30](https://github.com/sandovaldavid/auctions/commit/4f3db302d652971dc35f1ec324a53e2c0bbcf145))
* add script for code formatting and linting ([25994b9](https://github.com/sandovaldavid/auctions/commit/25994b902dc5317877e40d03267c1b44c20332ca))
* **api:** add API endpoints and documentation support ([07ae686](https://github.com/sandovaldavid/auctions/commit/07ae686ad7f03a9e33fd08984148197377cd3f0c))
* **api:** add auctions API with views, serializers and permissions ([1f5da95](https://github.com/sandovaldavid/auctions/commit/1f5da95659c32e17e5f47a2dfe6d443d9a4a7c96))
* Create a comprehensive Spanish README ([d9fbbb6](https://github.com/sandovaldavid/auctions/commit/d9fbbb6ed164dbd5e39ff1696579c087359c0c8a))
* **dashboard:** add business intelligence dashboard template ([2713895](https://github.com/sandovaldavid/auctions/commit/2713895b97f965000787bf0ad5b209c9b05731e5))
* **layout:** add search functionality and improve user dropdown ([a2485cc](https://github.com/sandovaldavid/auctions/commit/a2485ccab704b9f0011ec35cadaefcbe3fe3ba25))
* **middleware:** add rate limiting and security middleware ([85977f8](https://github.com/sandovaldavid/auctions/commit/85977f80cab9de54f9e596e4f3bd80d44306d20c))
* **models:** add notification system and improve model fields ([02c43bd](https://github.com/sandovaldavid/auctions/commit/02c43bdb31795b8daba3a484a6146fbbe696910f))
* **notifications:** add real-time notification system with websockets ([1259ef7](https://github.com/sandovaldavid/auctions/commit/1259ef78367ac1ec233a5696d988986fc1444158))
* **notifications:** implement real-time notification system ([cbb31d0](https://github.com/sandovaldavid/auctions/commit/cbb31d07c779cee4cd782087a63bbc710f42cb4c))
* **pagination:** add custom pagination class with configurable page size ([cddfb66](https://github.com/sandovaldavid/auctions/commit/cddfb6626b1390da587209684377ded6b3f95569))
* **profile:** add user profile page with stats and quick actions ([a69c432](https://github.com/sandovaldavid/auctions/commit/a69c432c68a8088ba56d3260cda0a2422b7bd4c5))
* **routing:** add websocket routing configuration for auctions notifications ([d958698](https://github.com/sandovaldavid/auctions/commit/d958698dce5c14e6d0e7399032648cf531518bce))
* **search:** add search page with advanced filters and autocomplete ([eec0c0b](https://github.com/sandovaldavid/auctions/commit/eec0c0b53b9ceaff3248b7f060786203a53585f6))
* **security:** add rate limiting decorator for API endpoints ([b1eeefa](https://github.com/sandovaldavid/auctions/commit/b1eeefaf003090c21dfad310de379404c29ec2ba))
* **settings:** add API, security, and async support to Django settings ([783381f](https://github.com/sandovaldavid/auctions/commit/783381f4ba2bc825bdce561df1c03c2d57fc7171))
* **styles:** add new profile, dashboard and search page styles with dark mode support ([a88f74e](https://github.com/sandovaldavid/auctions/commit/a88f74e770c90831b13427fc83c6c7880c86557a))
* **templates:** add list_item component and update alert/footer styles ([e115133](https://github.com/sandovaldavid/auctions/commit/e11513386ecb938c9a0fe81040b2f539b559fcd7))
* **templatetags:** add watchlist check and json conversion filters ([c7bc30d](https://github.com/sandovaldavid/auctions/commit/c7bc30db388e19245e5480e8ceed94bbf3f050dc))
* **urls:** add new endpoints and remove trailing slashes ([bb5bd17](https://github.com/sandovaldavid/auctions/commit/bb5bd17662bcb11435b52c2845ca59c8b1c85ca2))
* **websocket:** add websocket support for notifications ([d04cce9](https://github.com/sandovaldavid/auctions/commit/d04cce9c6af3ac35a7dd9b323d54ed7c4f72b00b))


### Bug Fixes

* **auctions:** correct bid view GET return and dynamic category choices ([d63b254](https://github.com/sandovaldavid/auctions/commit/d63b254ae3daf2498f769744487f83d55ec787f4)), closes [#17](https://github.com/sandovaldavid/auctions/issues/17)
* **auctions:** correct WCAG AA contrast ratios in light and dark themes ([#36](https://github.com/sandovaldavid/auctions/issues/36)) ([ca260e7](https://github.com/sandovaldavid/auctions/commit/ca260e7283854e700ff6d9e9d70ebb5cf0e64d91))
* **auctions:** import error_views for test error URL handlers in urls.py ([062edcc](https://github.com/sandovaldavid/auctions/commit/062edcc84b0f447ffc4f1f224fa2f63772f7a412))
* **auctions:** lazy-import analytics deps so app starts without numpy/pandas in prod ([573b0b0](https://github.com/sandovaldavid/auctions/commit/573b0b09df8d7614ae86ead2dffebc857a898e0c))
* **auctions:** lazy-import analytics deps so app starts without numpy/pandas in prod ([055f3a6](https://github.com/sandovaldavid/auctions/commit/055f3a67502795679fba3b92ce0ef6b1b388db70))
* **ci:** fix bandit format flag and add debug_toolbar URL config ([aa0d914](https://github.com/sandovaldavid/auctions/commit/aa0d914b7c2ebac76d168da8a65e62e33f6f81ee))
* **ci:** remove tag trigger from cd-production to prevent double-deploy ([fc43437](https://github.com/sandovaldavid/auctions/commit/fc4343788dcc697803bb3a41383eedede4bd4d2a))
* **ci:** replace deprecated heroku-deploy action with direct CLI install ([5a27151](https://github.com/sandovaldavid/auctions/commit/5a2715139bf7133fa18c7c18822671d3e3b5ed7a))
* **ci:** replace deprecated heroku-deploy action with direct CLI install ([#31](https://github.com/sandovaldavid/auctions/issues/31)) ([07fe95a](https://github.com/sandovaldavid/auctions/commit/07fe95ac0456d1d74889f9c4d00d10b512c61b3f))
* **ci:** resolve all ruff lint errors and format with black ([37f5d28](https://github.com/sandovaldavid/auctions/commit/37f5d284cdb791479293165e01858c9686751874))
* **ci:** set heroku container stack before pushing Docker image ([ff43012](https://github.com/sandovaldavid/auctions/commit/ff4301299de4344bf20e829845e78f2bf3bf353b))
* **ci:** set heroku container stack before pushing Docker image ([#33](https://github.com/sandovaldavid/auctions/issues/33)) ([ae8b82d](https://github.com/sandovaldavid/auctions/commit/ae8b82d84e211a9ab5d2fb54108cc01a02ce3b47))
* **docker:** add heroku release phase for migrations and auto-detect dyno host ([1787161](https://github.com/sandovaldavid/auctions/commit/17871611418554a6830ced5023f89ff63c03b214))
* **docker:** fix port binding and add release phase for Heroku deploy ([63c9d0b](https://github.com/sandovaldavid/auctions/commit/63c9d0b8eace7700245a4a4dc6df798fe987c095))
* **docker:** use shell form CMD so $PORT expands on Heroku ([27cbc0f](https://github.com/sandovaldavid/auctions/commit/27cbc0f80ee5145eddd5a6e1a27fdebf14530d27))
* Link variables.css to enable theme switching ([8706252](https://github.com/sandovaldavid/auctions/commit/8706252c82564d937b44aed3d1df64a43a26c8ed))
* remove duplicate title validation and debug print ([f2be7c4](https://github.com/sandovaldavid/auctions/commit/f2be7c4cfc9f3038f35a801dd8dc01a6a34a1603))
* **tests:** fix 5 failing tests and exclude extra files from coverage ([45f16fa](https://github.com/sandovaldavid/auctions/commit/45f16fa034d181eaad8c3cd856b80944c27e51b4))


### Documentation

* add key features walkthrough documentation ([f136ea6](https://github.com/sandovaldavid/auctions/commit/f136ea6fe04e5a75759ff61ba9ad804a5c287d32))
* add project description and role documentation ([3025a8f](https://github.com/sandovaldavid/auctions/commit/3025a8f676d6000fd0982bfa1402720c6752ad8a))
* add system architecture documentation ([3d3a86a](https://github.com/sandovaldavid/auctions/commit/3d3a86affbe35b9e5458076a6504bc633aec9f59))
* add technical challenges and solutions documentation ([c5df6ad](https://github.com/sandovaldavid/auctions/commit/c5df6ad0392c06ca060d754cc757103a1f988e76))
* add technical interview preparation guide ([f8eeab0](https://github.com/sandovaldavid/auctions/commit/f8eeab0db983c03e4e1e56a393f8397e981bae1b))
* add technical presentation guide for auction platform ([6e90069](https://github.com/sandovaldavid/auctions/commit/6e90069c37cd593a6209838c0b8d779340f769ec))

## [0.2.0](https://github.com/sandovaldavid/auctions/compare/v0.1.0...v0.2.0) (2026-06-20)


### Features

* **auctions:** merge develop into main — v0.1.1 ([#45](https://github.com/sandovaldavid/auctions/issues/45)) ([e4a837b](https://github.com/sandovaldavid/auctions/commit/e4a837b612b9c58729029f69b875deb3424e220b))

## [0.1.1](https://github.com/sandovaldavid/auctions/compare/v0.1.0...v0.1.1) (2026-06-20)


### Bug Fixes

* **auctions:** correct WCAG AA contrast ratios in light and dark themes ([#36](https://github.com/sandovaldavid/auctions/issues/36)) ([ca260e7](https://github.com/sandovaldavid/auctions/commit/ca260e7283854e700ff6d9e9d70ebb5cf0e64d91))

## 0.1.0 (2026-06-20)


### Features

* Create a comprehensive Spanish README ([d9fbbb6](https://github.com/sandovaldavid/auctions/commit/d9fbbb6ed164dbd5e39ff1696579c087359c0c8a))


### Bug Fixes

* **auctions:** lazy-import analytics deps so app starts without numpy/pandas in prod ([573b0b0](https://github.com/sandovaldavid/auctions/commit/573b0b09df8d7614ae86ead2dffebc857a898e0c))
* **ci:** replace deprecated heroku-deploy action with direct CLI install ([#31](https://github.com/sandovaldavid/auctions/issues/31)) ([07fe95a](https://github.com/sandovaldavid/auctions/commit/07fe95ac0456d1d74889f9c4d00d10b512c61b3f))
* **ci:** set heroku container stack before pushing Docker image ([#33](https://github.com/sandovaldavid/auctions/issues/33)) ([ae8b82d](https://github.com/sandovaldavid/auctions/commit/ae8b82d84e211a9ab5d2fb54108cc01a02ce3b47))
* **docker:** fix port binding and add release phase for Heroku deploy ([63c9d0b](https://github.com/sandovaldavid/auctions/commit/63c9d0b8eace7700245a4a4dc6df798fe987c095))
