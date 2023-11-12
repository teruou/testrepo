\l …… データベースの一覧
\c データベース …… データベースを切り替える
\d …… テーブル、ビュー、シーケンスの一覧
\dt …… テーブル一覧
\ds …… シーケンス一覧
\dv …… ビュー一覧
\di …… インデックス一覧
\d 名前 …… 指定したテーブル、ビュー、シーケンス、インデックスの定義
\i ファイル …… ファイルに記述された SQL を実行する
\q …… コマンドラインツールを終了する
\? …… ヘルプを表示
select version();
\du
\db
\dn+
すべてのテーブルの統計情報の最後の更新日時を確認できます
SELECT max(last_analyze) AS last_analyze
FROM pg_stat_all_tables;

SELECT relname, 
       last_vacuum, 
       last_autovacuum, 
       last_analyze, 
       last_autoanalyze
FROM pg_stat_user_tables;

SELECT relname AS table_name, schemaname, last_analyze, last_autoanalyze
FROM pg_stat_all_tables
WHERE schemaname = 'public' -- 任意のスキーマ名に変更可能
ORDER BY last_analyze DESC;

You
aws aurora postgresqlでセキュリティ上、publicは無効にすべきか？
　
　
AWS Aurora PostgreSQL において、セキュリティ上のベストプラクティスは、原則として最小権限の原則（Principle of Least Privilege）に従うことです。これは、ユーザーやアプリケーションが必要とする最小限の権限のみを付与するという方針です。この原則に従うと、public スキーマのデフォルトのアクセス権を制限することが推奨されます。

PostgreSQLでは、新たに作成されるデータベースにはデフォルトで public スキーマが存在し、このスキーマには初期状態で全ユーザーがアクセスできる権限が付与されています。これにより、新しいオブジェクトがこのスキーマに自由に作成できるなど、セキュリティ上の問題が生じる可能性があります。

セキュリティを強化するために、以下のような手順を踏むことが一般的です：

public スキーマからデフォルトの権限を削除する：
データベース内の全ユーザーが public スキーマに対して持つ権限を削除します。これにより、新たに作成されるユーザーにはこのスキーマへのアクセス権が自動的に付与されなくなります。

sql
Copy code
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE yourdbname FROM PUBLIC;
必要なユーザーにのみ権限を付与する：
特定のユーザーやグループにのみ必要な権限を付与します。たとえば、特定のユーザーにのみ public スキーマへのアクセス権を与えることができます。

専用のスキーマの使用：
public スキーマを全く使用せず、各ユーザーやアプリケーション専用のスキーマを作成し、そこにのみ必要な権限を付与することができます。

セキュリティグループとネットワークACLの設定：
AWSのセキュリティグループやネットワークアクセス制御リスト（ACL）を設定して、データベースインスタンスへの不要なトラフィックをブロックします。

IAMを使ったデータベース認証：
AWS Identity and Access Management（IAM）を利用して、データベースへの認証を管理します。

セキュリティは多層的に考えるべきであり、
単一の措置ではなく、総合的なセキュリティ対策が求められます。
これには、アクセス権限の管理のみならず、ネットワークのセキュリティ、暗号化、監視といった側面が含まれます。
また、AWSのドキュメントやセキュリティガイドラインを参考にしながら、環境に最適なセキュリティ設定を行ってください。
