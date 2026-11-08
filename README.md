# timetable-tool

Googleカレンダーの予定を読み取り、今週（または来週）の時間割をMarkdownで出力するPythonツール。

OAuth不要で、Googleカレンダーの「iCal形式の秘密のアドレス」（ICS）を使って予定を取得します。繰り返し予定の展開にも対応しています。

## 使い方

### 1. ライブラリを入れる

```bash
pip install requests icalendar recurring-ical-events
```

### 2. ICSアドレスを設定する

1. Googleカレンダーを開き、設定 → 対象カレンダー →「カレンダーの統合」→「iCal形式の秘密のアドレス」をコピー
2. `config.example.json` を `config.json` にコピーし、コピーしたアドレスを貼る（複数カレンダーも可）

⚠️ 秘密のアドレスは「知っている人が予定を全部見られる鍵」です。`config.json` は `.gitignore` で除外してあるので、GitHubに上げないでください。

### 3. 実行する

```bash
python timetable.py          # 今週の時間割
python timetable.py --next   # 来週の時間割
```

コンソールに表示され、あわせて `timetable.md` にも書き出されます。Notionなどにそのまま貼れます。

## 出力例

```markdown
# 今週の時間割（11/09〜11/15）

## 11/09（月）
- 09:00–13:30 インターン
- 14:50–16:40 コンパイラ
```

## 技術メモ

- 繰り返し予定（RRULE）の週内展開には `recurring-ical-events` を使用
- 日時はすべて Asia/Tokyo にそろえて表示
- 複数カレンダーを読んだ場合、同一予定の重複は自動で除去

## 作者

太田海翔（電気・情報系の大学3年生）
