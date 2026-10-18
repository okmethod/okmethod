---
description: Svelte 5 の開発規約（Runes・Tailwind・effect）。全PJ共通の核
globs:
  - "practices/**/*.svelte"
---

# Svelte 5

> このファイルは全PJ共通の核。言語非依存の規約は `coding-guide.md` が SSoT。
> 各PJでは SvelteKit / Skeleton / Vite のバージョンや固有ルール（レイヤー依存・ナビゲーション等）を別途追記する。

## 開発規約

- Runes 記法に統一する（旧 `let`/`$:` 記法は使わない）
  - リアクティブ変数: `let x = $state(0)`
  - 算出値: `const y = $derived(...)`
  - 副作用: `$effect(() => { ... })`
  - Props: `let { a, b } = $props()`（`interface XxxProps` を定義してから使う）
- 同ファイル内の繰り返し UI は `{#snippet}` / `{@render}` を優先検討する
- スタイリングは TailwindCSS ユーティリティクラスのみ。`<style>` ブロックは書かない
  - 動的クラスは文字列リテラルで定義する（テンプレート文字列での動的生成は Tailwind スキャナーに検出されないため NG）
- `$effect` で DOM 操作が必要な場合は `tick()` を await してから実行する
- `bind:this` が不安定な場合は `use:` ディレクティブで要素を登録する
