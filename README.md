# ユーザーに元データの最大バイト数を入力させる
$B = Read-Host "元データの最大バイト数 (B) を入力してください"

# 入力された値が数値かどうかを確認する
if (![int]::TryParse($B, [ref]0)) {
    Write-Host "数値を入力してください"
    exit
}

# 暗号化列長の計算
$encryptedLength = 16 * ([Math]::Truncate($B / 16) + 1)

# 結果を表示
Write-Host "暗号化列長（バイト）: $encryptedLength"
