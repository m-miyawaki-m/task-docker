# Chocolatey エディション比較

Chocolatey には無料版と有料版があり、機能が大きく異なる。特にオフライン環境での利用を検討する場合、有料版の機能を理解することが重要。

## エディション一覧

| エディション | 価格 | 主な対象 |
|-------------|------|---------|
| **Chocolatey Open Source (FOSS)** | 無料 | 個人・小規模チーム |
| **Chocolatey Pro** | $96/年/ユーザー | 個人・パワーユーザー |
| **Chocolatey Business (C4B)** | 要問合せ（$500+/年/ノード目安） | 企業・組織 |

---

## 各エディションの機能

### Chocolatey Open Source（無料版）

基本的なパッケージ管理機能:

- `choco install` / `choco uninstall` / `choco upgrade`
- 公開リポジトリ（community.chocolatey.org）からのインストール
- ローカルリポジトリの利用
- 基本的な依存関係解決

**制限事項:**
- マルウェア保護なし
- パッケージ自動作成機能なし
- 企業向け管理機能なし

---

### Chocolatey Pro

Pro の主な追加機能:

| 機能 | 説明 |
|------|------|
| **Runtime Malware Protection** | インストール時にVirusTotalでマルウェアスキャン |
| **Package Throttle** | ダウンロード帯域制御 |
| **Package Synchronizer** | 「プログラムと機能」との自動同期 |
| **Package Builder** | 既存の exe/msi から自動でパッケージ作成 |
| **Package Reducer** | パッケージサイズ削減（インストーラー削除等） |
| **優先サポート** | メールサポート対応 |

```powershell
# Pro版: 既存インストーラーからパッケージ自動生成
choco new myapp --file="C:\Downloads\myapp-installer.exe" --build-package
```

---

### Chocolatey Business (C4B)

Pro の全機能に加えて、企業向け管理機能を追加:

#### 管理・運用機能

| 機能 | 説明 |
|------|------|
| **Chocolatey Central Management (CCM)** | Web UIでの一元管理・ダッシュボード |
| **Deployment Scheduling** | パッケージ配布のスケジュール設定 |
| **Package Audit** | インストール履歴の監査ログ |
| **Directory Services Integration** | Active Directory / LDAP 連携 |

#### セキュリティ・コンプライアンス

| 機能 | 説明 |
|------|------|
| **Package Internalizer** | 公開パッケージを内部用に自動変換 |
| **Self-Service GUI** | 非管理者向けの承認済みソフトウェアインストール画面 |
| **CDN Cache** | パッケージキャッシュによる高速配布 |

---

## オフライン環境での重要機能: Package Internalizer

### Package Internalizer とは

公開リポジトリのパッケージを、オフライン環境向けに自動変換する機能。

**通常のパッケージの問題:**
```
chocolateyinstall.ps1 内で外部URLからダウンロード
  ↓
$url = 'https://github.com/git-for-windows/git/releases/download/...'
Install-ChocolateyPackage ... -Url $url
  ↓
オフライン環境では失敗
```

**Internalizer が解決:**
```powershell
# Business版: パッケージを自動で内部化
choco download git --internalize --source="'https://community.chocolatey.org/api/v2/'"
```

実行結果:
1. パッケージをダウンロード
2. スクリプト内の外部URLを検出
3. バイナリを自動ダウンロード
4. パッケージ内に埋め込み
5. スクリプトをローカル参照に書き換え

### 無料版でのオフライン対応（手動作業）

Internalizer がない場合、以下を手動で行う必要がある:

```
1. nupkg をダウンロード
2. 解凍して chocolateyinstall.ps1 を確認
3. スクリプト内のダウンロードURLを特定
4. バイナリを手動ダウンロード
5. スクリプトをローカルパス参照に書き換え
6. nuspec のバージョン等を調整
7. choco pack で再パッケージ
8. ローカルリポジトリに配置
```

**数十ツールでこの作業を行うのは非現実的。**

---

## エディション別 機能比較表

| 機能 | FOSS | Pro | Business |
|------|:----:|:---:|:--------:|
| 基本インストール/アンインストール | ✓ | ✓ | ✓ |
| 公開リポジトリ利用 | ✓ | ✓ | ✓ |
| ローカルリポジトリ | ✓ | ✓ | ✓ |
| マルウェアスキャン | - | ✓ | ✓ |
| 帯域制御 | - | ✓ | ✓ |
| Package Builder（自動作成） | - | ✓ | ✓ |
| Package Synchronizer | - | ✓ | ✓ |
| **Package Internalizer** | - | - | ✓ |
| Central Management (CCM) | - | - | ✓ |
| Self-Service GUI | - | - | ✓ |
| AD/LDAP連携 | - | - | ✓ |
| 監査ログ | - | - | ✓ |

---

## 価格の目安（2024年時点）

| エディション | 価格体系 | 備考 |
|-------------|---------|------|
| **Open Source** | 無料 | 商用利用可 |
| **Pro** | $96/年/ユーザー | 個人ライセンス |
| **Business** | 要見積もり | ノード数ベース、最小$500+/年目安 |

※ Business は組織規模により価格が変動。正確な見積もりは公式へ問い合わせ。

---

## 判断フローチャート

```
オフライン環境で使う？
├── No → Chocolatey FOSS（無料）で十分
└── Yes
    ├── 予算がある？
    │   ├── Yes → Chocolatey Business を検討
    │   │         （ただしツール設定管理は別途必要）
    │   └── No → 自作スクリプト推奨
    └── ツール内部設定も管理したい？
        └── Yes → Chocolatey では対応不可
                  → 自作スクリプト（CSV + PowerShell）
```

---

## 結論

| 状況 | 推奨アプローチ |
|------|---------------|
| オンライン環境・個人利用 | Chocolatey FOSS（無料） |
| オンライン環境・企業で一元管理したい | Chocolatey Business |
| オフライン環境・予算あり・インストールのみ | Chocolatey Business 検討の余地あり |
| オフライン環境・予算なし | **自作スクリプト（CSV + PowerShell）** |
| オフライン環境・ツール設定も管理 | **自作スクリプト一択** |

### 今回の要件との照合

今回の要件:
- ✓ オフライン環境
- ✓ ツール内部設定管理（Eclipse formatter、SQLDeveloper接続情報等）
- ✓ バージョン不一致検知
- ✓ 環境変数設定

**Chocolatey Business でも「ツール内部設定管理」は対応不可のため、自作スクリプトが最適解。**

---

## 参考リンク

- [Chocolatey公式 - エディション比較](https://chocolatey.org/compare)
- [Chocolatey Business 機能一覧](https://chocolatey.org/products/chocolatey-for-business)
- [Package Internalizer ドキュメント](https://docs.chocolatey.org/en-us/features/package-internalizer)
