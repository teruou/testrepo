using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Support.UI;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using AdvanceSoftware.ExcelCreator;
using System.Reflection;
using AdvanceSoftware.PDF;
using static System.Net.Mime.MediaTypeNames;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.StartPanel;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace report
{
    public partial class Form1 : Form
    {
        // これらの変数をクラスレベルで宣言
        private string outputFilePath;
        private string inputFilePath;
        private string logFilePath;
        private string capturePath;
        private IWebDriver _WebDriver;
        private string selectedUserName;
        private string selectedUserId;
        private string selectedPassword;
        private string selectedscreenId;
        private string identifier;

        /// <summary>
        /// IniParser クラスは、INI 形式の設定ファイルを解析するためのクラスです。
        /// このクラスは、セクションとキーに基づいて設定値を取得する機能を提供します。
        /// </summary>
        public class IniParser
        {
            // セクション名をキーとし、そのセクション内のキーと値のペアを格納する辞書
            private readonly Dictionary<string, Dictionary<string, string>> sections = new();

            /// <summary>
            /// コンストラクタ。指定されたパスのINIファイルを読み込み、解析します。
            /// </summary>
            /// <param name="path">INIファイルのパス</param>
            public IniParser(string path)
            {
                // 現在解析中のセクションのキーと値を格納する辞書
                var currentSection = new Dictionary<string, string>();

                // ファイルの各行を読み込み
                foreach (var line in File.ReadAllLines(path))
                {
                    // セクションの開始行かどうかを判定
                    if (line.StartsWith("[") && line.EndsWith("]"))
                    {
                        // 新しいセクションが始まるため、currentSection を新しい辞書で初期化
                        currentSection = new Dictionary<string, string>();
                        // セクション名を抽出して、そのセクションの辞書を sections に追加
                        sections[line[1..^1]] = currentSection;
                    }
                    else
                    {
                        // キーと値を分割
                        var parts = line.Split('=', StringSplitOptions.TrimEntries);
                        // キーと値が正しく分割できた場合、currentSection に追加
                        if (parts.Length == 2)
                        {
                            currentSection[parts[0]] = parts[1];
                        }
                    }
                }
            }

            /// <summary>
            /// 指定されたセクションとキーに対応する値を取得します。
            /// </summary>
            /// <param name="section">セクション名</param>
            /// <param name="key">キー名</param>
            /// <returns>対応する値。見つからない場合は null。</returns>
            public string GetValue(string section, string key)
            {
                // 指定されたセクションが存在するか確認
                if (sections.TryGetValue(section, out var sectionDict))
                {
                    // セクション内で指定されたキーに対応する値が存在するか確認
                    if (sectionDict.TryGetValue(key, out var value))
                    {
                        return value;
                    }
                }
                return null;
            }
        }
        public Form1()
        {
            InitializeComponent();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            if (_WebDriver != null)
            {
                _WebDriver.Quit();      //すべて閉じる
                _WebDriver.Dispose();
                _WebDriver = null;
            }
            // アプリケーションを終了
            System.Windows.Forms.Application.Exit();
        }
        public string CreateLogDirectoryAndFile(string localPath)
        {
            Directory.CreateDirectory(localPath);

            string logFilePath = Path.Combine(localPath, $"Sereniumlog_{GetCurrentDateTime()}.log");
            if (!File.Exists(logFilePath))
            {
                using (StreamWriter logFile = File.CreateText(logFilePath))
                {
                    logFile.WriteLine("Installation log");
                }
            }
            return logFilePath;
        }
        /// <summary>
        /// 現在のブラウザの画面をスクリーンショットとしてキャプチャし、指定されたディレクトリに保存します。
        /// 保存されるファイル名は、項番、テキスト、現在の日時を組み合わせたものになります。
        /// </summary>
        /// <param name="itemNumber">項番を示す文字列。</param>
        /// <param name="text">スクリーンショットの名前の一部として使用されるテキスト。</param>
        /// <param name="directoryPath">スクリーンショットを保存するディレクトリのパス。</param>
        public void TakeScreenshotAndSave(string itemNumber, string text, string directoryPath)
        {
            // ブラウザのウィンドウを全画面表示にする
            _WebDriver.Manage().Window.FullScreen();

            // スクリーンショットをキャプチャする
            Screenshot screenshot = (_WebDriver as ITakesScreenshot).GetScreenshot();

            // スクリーンショットの保存先のパスを生成
            string savePath = Path.Combine(directoryPath, $"{itemNumber}_{text}_{GetCurrentDateTime()}.png");

            // スクリーンショットを指定されたパスにPNG形式で保存する
            screenshot.SaveAsFile(savePath, ScreenshotImageFormat.Png);
        }

        /// <summary>
        /// ログファイルに指定された情報を追記します。
        /// </summary>
        /// <param name="itemNumber">項番を示す文字列。</param>
        /// <param name="text">ログに追加するテキスト。</param>
        /// <param name="messageBody">メッセージの本文。</param>
        public void AppendToLogFile(string itemNumber, string text, string messageBody)
        {

            string logTime = GetCurrentDateTime();
            try
            {
                using (StreamWriter logFile = new StreamWriter(logFilePath, append: true))
                {
                    logFile.WriteLine($"{logTime} 項番: {itemNumber}, 文字: {text}, メッセージ本文: {messageBody}");
                    logFile.WriteLine();
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"ファイルの書き込みに失敗しました: {logFilePath}\n{ex.Message}");
            }
        }



        public string GetCurrentDateTime()
        {
            return DateTime.Now.ToString("yyyy-MM-dd_HH_mm_ss");
        }
        private void button2_Click(object sender, EventArgs e)
        {
            string SheetName = "ログイン";
            int startRow = 6; // データの読み取りを開始する行
            int screencol = 2;
            int usercol = 3;
            int passwdcol = 4;
            int itemNumberCol = 1; // 項番が格納されている列のインデックス
            string targetItemNumber = textBox1.Text; // txtItemNumberは項番を入力するテキストボックスと仮定
                                                     //ライセンスファイルをファイルパスで指定する

            MessageBox.Show("ログインを開始します");
            var parser = new IniParser("Selenium.ini");
            Console.WriteLine($"TablePath: {parser.GetValue("Settings", "TablePath")}");
            Console.WriteLine($"outputPath: {parser.GetValue("Settings", "outputPath")}");

            //ログ作成
            string path = parser.GetValue("Settings", "outputPath");
            //メンバ変数に格納
            logFilePath = CreateLogDirectoryAndFile(path);

            AppendToLogFile("1-1", "ログイン", "自動テストを開始します");
                                       //creator1.SetLicense("C:\\Data\AdvanceSoftware.ExcelCreator.License.xml");

            if (string.IsNullOrWhiteSpace(targetItemNumber))
            {
                MessageBox.Show("ログイン名を入力してください。");
                return;
            }

            // ExcelCreator インスタンス生成
            this.components = new System.ComponentModel.Container();
            this.creator1 = new Creator(this.components);

            var srcPath = parser.GetValue("Settings", "TablePath"); // ここにExcelファイルのパスを指定
            creator1.OpenBook(srcPath, "");
            //シート切替
            creator1.SheetNo = creator1.SheetNo2(SheetName);
            //string screenId = creator1.Pos(3, 6).Value.ToString();
            //string userId = creator1.Pos(usercol, startRow).Value.ToString();
            //string password = creator1.Pos(passwdcol, startRow).Value.ToString();
            //string cellValue2 = creator1.Cell("A2").Value.ToString();
            //AppendToLogFile("xxx", "検索", cellValue2);
            int rowIndex = startRow;
            //ログ作成
            AppendToLogFile("xxx", "マッチしたもの", "テスト１");
            while (true)
            {
                //項番nullcheck
                var cell = creator1.Pos(1, rowIndex); // Cellオブジェクトを取得
                if (cell == null || cell.Value == null)
                {
                    break; // セルオブジェクトまたはセルの値がnullの場合、ループを終了
                }
                string cellValue = cell.Value.ToString();

                AppendToLogFile("xxx", "マッチしたもの", cellValue);

                // 指定された項番にマッチするか確認
                if (cellValue == targetItemNumber)
                {
                    //項番
                    //Itemnumber = creator1.Pos(0, rowIndex).Value?.ToString();
                    //ログイン名
                    //Testvoucher = creator1.Pos(1, rowIndex).Value?.ToString();
                    //識別子
                    identifier = creator1.Pos(2, rowIndex).Value?.ToString();
                    //ID
                    selectedUserId = creator1.Pos(3, rowIndex).Value?.ToString();
                    //password
                    selectedPassword = creator1.Pos(4, rowIndex).Value?.ToString();
                    //btn

                }

                rowIndex++;
            }


            // ここで必要な操作を行う。例えば:
            // MessageBox.Show($"User: {selectedUserName}\nUserID: {selectedUserId}\nPassword: {selectedPassword}");

            if (_WebDriver != null)
            {
                _WebDriver.Quit();      //すべて閉じる
                _WebDriver.Dispose();
                _WebDriver = null;
                System.Windows.Forms.Application.DoEvents(); //気分的にちょっと。。。
            }

            //サービス設定(コンソールを表示しない)
            ChromeDriverService service = ChromeDriverService.CreateDefaultService();
            service.HideCommandPromptWindow = true;

            //オプション設定(非表示にしたり、Userを選択したり)
            ChromeOptions options = new ChromeOptions();
            //options.AddArgument("--headless");    //非表示
            options.AddArgument("--start-maximized");   //最大化(Chromeのみ？)

            //instance生成
            _WebDriver = new ChromeDriver(service, options);

            //URLにアクセス
            _WebDriver.Navigate().GoToUrl(identifier);


            //　HTMLタグ内のIdから要素取得
            //IWebElement element = _WebDriver.FindElement(By.Id("loginForm"));

            //　取得した要素のうちnameを指定してログインIDとPASSWORを入力      
            // 入力
            var userElement = _WebDriver.FindElement(By.Name("user_id"));
            userElement.SendKeys(selectedUserId);
            var passElement = _WebDriver.FindElement(By.Name("user_password"));
            passElement.SendKeys(selectedPassword);
            //　ログインボタンをクリック
            //_WebDriver.FindElement(By.Id("login_button")).Click();
            _WebDriver.FindElement(By.Name("ACT_login")).Click();


            var wait = new WebDriverWait(_WebDriver, TimeSpan.FromSeconds(10)); // 10秒は例として挙げたもので、実際の最大待機時間を設定してください。
            IWebElement firstResult = wait.Until(webDriverElem => webDriverElem.FindElement(By.XPath("//*")));

        }
        public string GetColumnName(int columnIndex)
        {
            int dividend = columnIndex;
            string columnName = String.Empty;
            int modulo;

            while (dividend > 0)
            {
                modulo = (dividend - 1) % 26;
                columnName = Convert.ToChar(65 + modulo).ToString() + columnName;
                dividend = (int)((dividend - modulo) / 26);
            }

            return columnName;
        }
        public List<string[]> LoadExcel(string srcPath, string SheetName, int startRow)
        {
            // 結果を格納するためのリストを初期化
            var resultList = new List<string[]>();

            // ExcelCreator インスタンス生成
            this.components = new System.ComponentModel.Container();
            this.creator1 = new Creator(this.components);

            creator1.OpenBook(srcPath, "");
            creator1.SheetNo = creator1.SheetNo2(SheetName);

            // A列の最後の記入されているセルを探す
            int lastRow = 10; // Excelの最大行数を仮の上限として設定
            for (int r = startRow; r <= lastRow; r++)
            {
                if (string.IsNullOrEmpty(creator1.Pos(r, 1).ToString()))
                {
                    lastRow = r - 1;
                    break;
                }
            }

            // 指定された開始行からデータを読み取る
            for (int row = startRow; row <= lastRow; row++)
            {
                // 現在の行のデータを格納するためのリストを初期化
                var values = new List<string>();

                // 各列のデータを読み取る
                int col = 1;
                while (!string.IsNullOrEmpty(creator1.Pos(row, col).ToString()))
                {
                    // 現在のセルの値を取得
                    var cellValue = creator1.Pos(row, col).ToString();

                    // セルのテキストをリストに追加
                    values.Add(cellValue);
                    col++;
                }

                // 行のデータを結果のリストに追加
                resultList.Add(values.ToArray());
            }

            //Excel ファイルクローズ
            creator1.CloseBook(true);

            // 結果のリストを返す
            return resultList;
        }


        private void button1_Click(object sender, EventArgs e)
        {

            try
            {

                var parser = new IniParser("Selenium.ini");
                Console.WriteLine($"TablePath: {parser.GetValue("Settings", "TablePath")}");
                Console.WriteLine($"outputPath: {parser.GetValue("Settings", "outputPath")}");

                //ログ作成
                string path = parser.GetValue("Settings", "outputPath");
                //メンバ変数に格納
                logFilePath = CreateLogDirectoryAndFile(path);

                AppendToLogFile("1-1", "検索", "自動テストを開始します");

                //LoadUsersFromExcel();

                if (_WebDriver != null)
                {
                    _WebDriver.Quit();      //すべて閉じる
                    _WebDriver.Dispose();
                    _WebDriver = null;
                    System.Windows.Forms.Application.DoEvents(); //気分的にちょっと。。。
                }

                //selenium起動
                //サービス設定(コンソールを表示しない)
                ChromeDriverService service = ChromeDriverService.CreateDefaultService();
                service.HideCommandPromptWindow = true;

                //オプション設定(非表示にしたり、Userを選択したり)
                ChromeOptions options = new ChromeOptions();
                //options.AddArgument("--headless");    //非表示
                options.AddArgument("--start-maximized");   //最大化(Chromeのみ？)

                //instance生成
                _WebDriver = new ChromeDriver(service, options);

                string screenId = "https://dashboard.e-stat.go.jp/graphSearch";
                //URLにアクセス
                _WebDriver.Navigate().GoToUrl(screenId);


                var srcPath = parser.GetValue("Settings", "TablePath"); // ここにExcelファイルのパスを指定
                string SheetName = "志望者検索";
                int startRow = 4; // データの読み取りを開始する行
                int screencol = 2;
                int usercol = 3;
                int passwdcol = 4;

                // ExcelCreator インスタンス生成
                this.components = new System.ComponentModel.Container();
                this.creator1 = new Creator(this.components);

                creator1.OpenBook(srcPath, "");
                creator1.SheetNo = creator1.SheetNo2(SheetName);
                //string screenId = creator1.Pos(screencol, startRow).Value.ToString();
                //string userId = creator1.Pos(usercol, startRow).Value.ToString();
                //string password = creator1.Pos(passwdcol, startRow).Value.ToString();
                MessageBox.Show("処理を開始します");
                // D列からデータがある列までループ
                int colIndex = 3; // D列はインデックス3
                while (creator1.Pos(colIndex, 3).Value != null && !string.IsNullOrEmpty(creator1.Pos(colIndex, 3).Value.ToString()))
                {
                    // 5行目（種別）のセルの値を取得
                    string type = creator1.Pos(colIndex, 4).Value.ToString();

                    // 6行目（識別子）のセルの値を変数に格納
                    string identifier = creator1.Pos(colIndex, 5).Value?.ToString();

                    // 7行目以降のセルをループ
                    int rowIndex = 6;
                    while (creator1.Pos(colIndex, rowIndex).Value != null && !string.IsNullOrEmpty(creator1.Pos(colIndex, rowIndex).Value.ToString()))
                    {
                        string cellValue = creator1.Pos(colIndex, rowIndex).Value.ToString();

                        if (type == "Xpath")
                        {
                            // XPathの場合の処理
                            if (cellValue == "ON" || !string.IsNullOrEmpty(cellValue) && cellValue != "OFF")
                            {
                                // "ON"または"文字数字"が入力されている場合の処理
                                // ここに処理を追加してください
                                AppendToLogFile("XPath", colIndex.ToString(), identifier);
                                IWebElement aoOption = _WebDriver.FindElement(By.XPath(identifier));
                                ((IJavaScriptExecutor)_WebDriver).ExecuteScript("arguments[0].click();", aoOption);
                                //screenshot メンバ変数から取得
                                // TakeScreenshotAndSave("1-1", colIndex.ToString(), logFilePath);
                            }
                        }
                        else if (type == "ID")
                        {
                            // IDの場合の処理
                            if (cellValue != "OFF")
                            {
                                // OFF以外の文字数字が入力されている場合の処理
                                // ここに処理を追加してください
                                AppendToLogFile("ID", colIndex.ToString(), identifier);
                                //　取得した要素のうちnameを指定してログインIDとPASSWORを入力      
                                // 入力
                                //var userElement = _WebDriver.FindElement(By.Id("c_code"));
                                //userElement.SendKeys(selectedUserId);
                                //var passElement = _WebDriver.FindElement(By.Id("c_pass"));
                                //passElement.SendKeys(selectedPassword);
                                //　ログインボタンをクリック
                                //_WebDriver.FindElement(By.Id("login_button")).Click();
                                //_WebDriver.FindElement(By.Name("bOK")).Click();

                                //var wait = new WebDriverWait(_WebDriver, TimeSpan.FromSeconds(10)); // 10秒は例として挙げたもので、実際の最大待機時間を設定してください。
                                //IWebElement firstResult = wait.Until(webDriverElem => webDriverElem.FindElement(By.XPath("//*")));

                            }
                        }

                        rowIndex++; // 次の行へ
                    }

                    colIndex++; // 次の列へ
                }

                MessageBox.Show("処理を終了します");

            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"エラーが発生しました: {ex.Message}\n\n詳細: {ex.StackTrace}");
                AppendToLogFile("9999", "エラー", $"エラーが発生しました: {ex.Message}\n\n詳細: {ex.StackTrace}");
            }


        }

        private void button4_Click(object sender, EventArgs e)
        {

            //SBIbank
            if (_WebDriver != null)
            {
                _WebDriver.Quit();      //すべて閉じる
                _WebDriver.Dispose();
                _WebDriver = null;
                System.Windows.Forms.Application.DoEvents(); //気分的にちょっと。。。
            }

            //サービス設定(コンソールを表示しない)
            ChromeDriverService service = ChromeDriverService.CreateDefaultService();
            service.HideCommandPromptWindow = true;

            //オプション設定(非表示にしたり、Userを選択したり)
            ChromeOptions options = new ChromeOptions();
            //options.AddArgument("--headless");    //非表示
            options.AddArgument("--start-maximized");   //最大化(Chromeのみ？)

            //instance生成
            _WebDriver = new ChromeDriver(service, options);

            //URLにアクセス
            _WebDriver.Navigate().GoToUrl(selectedscreenId);


            //　HTMLタグ内のIdから要素取得
            //IWebElement element = _WebDriver.FindElement(By.Id("loginForm"));

            //　取得した要素のうちnameを指定してログインIDとPASSWORを入力      
            // 入力
            var userElement = _WebDriver.FindElement(By.Name("userNameNewLogin"));
            userElement.SendKeys(selectedUserId);
            var passElement = _WebDriver.FindElement(By.Id("loginPwdSet"));
            passElement.SendKeys(selectedPassword);
            //　ログインボタンをクリック
            //_WebDriver.FindElement(By.Id("login_button")).Click();
            _WebDriver.FindElement(By.XPath("/html/body/app/div[1]/ng-component/div/main/ng-component/form/section[1]/div/div/ul/li/nb-button-login/button")).Click();


            var wait = new WebDriverWait(_WebDriver, TimeSpan.FromSeconds(10)); // 10秒は例として挙げたもので、実際の最大待機時間を設定してください。
            IWebElement firstResult = wait.Until(webDriverElem => webDriverElem.FindElement(By.XPath("//*")));







        }

        private void cmd_boatrace_Click(object sender, EventArgs e)
        {

            if (_WebDriver != null)
            {
                _WebDriver.Quit();      //すべて閉じる
                _WebDriver.Dispose();
                _WebDriver = null;
                System.Windows.Forms.Application.DoEvents(); //気分的にちょっと。。。
            }

            //サービス設定(コンソールを表示しない)
            ChromeDriverService service = ChromeDriverService.CreateDefaultService();
            service.HideCommandPromptWindow = true;

            //オプション設定(非表示にしたり、Userを選択したり)
            ChromeOptions options = new ChromeOptions();
            //options.AddArgument("--headless");    //非表示
            options.AddArgument("--start-maximized");   //最大化(Chromeのみ？)

            //instance生成
            _WebDriver = new ChromeDriver(service, options);


            IWebElement selectElement = _WebDriver.FindElement(By.Name("date_year"));
            //チェックボックス、ラジオボタン
            //_WebDriver.FindElement(By.XPath("/html/body/center/form/table/tbody/tr[1]/td[3]/select/option[2]")).Click();
            var selectObject = new SelectElement(selectElement);

            // Select an <option> based upon its text
            selectObject.SelectByText("2019年");

        }


        private void Form1_Load(object sender, EventArgs e)
        {

        }



        private void button5_Click(object sender, EventArgs e)
        {
            //検索
            try
            {
                MessageBox.Show("検索を開始します");
                var srcPath = @"C:\C_DEV\login_info.xlsx"; // ここにExcelファイルのパスを指定
                string SheetName = "志望者索引簿";
                int startRow = 2; // データの読み取りを開始する行
                int screencol = 2;
                int usercol = 3;
                int passwdcol = 4;
                int itemNumberCol = 1; // 項番が格納されている列のインデックス
                string targetItemNumber = textBox1.Text; // txtItemNumberは項番を入力するテキストボックスと仮定
                                                         //ライセンスファイルをファイルパスで指定する
                                                         //creator1.SetLicense("C:\\Data\AdvanceSoftware.ExcelCreator.License.xml");

                if (string.IsNullOrWhiteSpace(targetItemNumber))
                {
                    MessageBox.Show("項番を入力してください。");
                    return;
                }

                // ExcelCreator インスタンス生成
                this.components = new System.ComponentModel.Container();
                this.creator1 = new Creator(this.components);

                creator1.OpenBook(srcPath, "");
                //シート切替
                creator1.SheetNo = creator1.SheetNo2(SheetName);
                //string screenId = creator1.Pos(screencol, startRow).Value.ToString();
                //string userId = creator1.Pos(usercol, startRow).Value.ToString();
                //string password = creator1.Pos(passwdcol, startRow).Value.ToString();
                //string cellValue2 = creator1.Cell("A2").Value.ToString();
                //AppendToLogFile("xxx", "検索", cellValue2);
                int rowIndex = startRow;
                //ログ作成
                string path = @"C:\C_DEV\report_excelcre\log";
                logFilePath = CreateLogDirectoryAndFile(path);
                AppendToLogFile("xxx", "マッチしたもの", "テスト１");
                while (true)
                {
                    //項番nullcheck
                    var cell = creator1.Cell($"A{rowIndex}");
                    if (cell == null || cell.Value == null || string.IsNullOrEmpty(cell.Value.ToString()))
                    {
                        break; // セルが空の場合、ループを終了
                    }
                    string cellValue = cell.Value.ToString();

                    AppendToLogFile("xxx", "マッチしたもの", cellValue);


                    // 指定された項番にマッチするか確認
                    if (cellValue == targetItemNumber)
                    {
                        //項番
                        string Itemnumber = creator1.Cell($"A{rowIndex}").Value?.ToString();

                    }

                    rowIndex++;
                }

                MessageBox.Show("検索を終了します");
                // ここで必要な操作を行う。例えば:
                // MessageBox.Show($"User: {selectedUserName}\nUserID: {selectedUserId}\nPassword: {selectedPassword}");
            }
            catch (System.Exception ex)
            {
                MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                //Excel ファイルクローズ
                creator1.CloseBook(true);
            }
        }


    }

}
