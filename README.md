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
        public string CreateLogDirectoryAndFile()
        {
            string localPath = @"C:\C_DEV\report_excelcre\log";
            Directory.CreateDirectory(localPath);

            logFilePath = Path.Combine(localPath, $"Sereniumlog_{GetCurrentDateTime()}.log");
            if (!File.Exists(logFilePath))
            {
                using (StreamWriter logFile = File.CreateText(logFilePath))
                {
                    logFile.WriteLine("Installation log");
                }
            }
            return logFilePath;
        }
        public void TakeScreenshotAndSave(string itemNumber, string text, string directoryPath)
        {
            _WebDriver.Manage().Window.FullScreen();
            Screenshot screenshot = (_WebDriver as ITakesScreenshot).GetScreenshot();
            string savePath = Path.Combine(directoryPath, $"{itemNumber}_{text}_{GetCurrentDateTime()}.png");
            screenshot.SaveAsFile(savePath, ScreenshotImageFormat.Png);
        }


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
                string logFilePath = CreateLogDirectoryAndFile();
                AppendToLogFile("1-1", "ログイン", "自動テストを開始します");


                var srcPath = @"C:\C_DEV\login_info.xlsx"; // ここにExcelファイルのパスを指定
                string SheetName = "ログイン情報";
                int startRow = 2; // データの読み取りを開始する行
                int screencol = 2;
                int usercol = 3;
                int passwdcol = 4;

                // ExcelCreator インスタンス生成
                this.components = new System.ComponentModel.Container();
                this.creator1 = new Creator(this.components);

                creator1.OpenBook(srcPath, "");
                creator1.SheetNo = creator1.SheetNo2(SheetName);
                string screenId = creator1.Pos(screencol, startRow).Value.ToString();
                string userId = creator1.Pos(usercol, startRow).Value.ToString();
                string password = creator1.Pos(passwdcol, startRow).Value.ToString();

                // string screenId = creator1.Cell("C2").Value.ToString();
                // string userId = creator1.Cell("D2").Value.ToString();
                // string password = creator1.Cell("E2").Value.ToString();
                // AppendToLogFile($"画面ID: {screenId}");
                // AppendToLogFile($"ユーザーID: {userId}");
                // AppendToLogFile($"パスワード: {password}");

                //Excel ファイルクローズ
                creator1.CloseBook(true);

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
                _WebDriver.Navigate().GoToUrl(screenId);
                //　取得した要素のうちnameを指定してログインIDとPASSWORを入力      
                // 入力
                var userElement = _WebDriver.FindElement(By.Id("c_code"));
                userElement.SendKeys(userId);
                var passElement = _WebDriver.FindElement(By.Id("c_pass"));
                passElement.SendKeys(password);
                //　ログインボタンをクリック
                //_WebDriver.FindElement(By.Id("login_button")).Click();
                _WebDriver.FindElement(By.Name("bOK")).Click();

                var wait = new WebDriverWait(_WebDriver, TimeSpan.FromSeconds(10)); // 10秒は例として挙げたもので、実際の最大待機時間を設定してください。
                IWebElement firstResult = wait.Until(webDriverElem => webDriverElem.FindElement(By.XPath("//*")));

                capturePath = @"C:\C_DEV\report_excelcre";
                TakeScreenshotAndSave("1-1", "ログイン", capturePath);

                _WebDriver.FindElement(By.Name("bOK")).Click();


            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"エラーが発生しました: {ex.Message}\n\n詳細: {ex.StackTrace}");
                AppendToLogFile("9999", "エラー", $"エラーが発生しました: {ex.Message}\n\n詳細: {ex.StackTrace}");
            }


        }

        private void button4_Click(object sender, EventArgs e)
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

            //URLにアクセス
            _WebDriver.Navigate().GoToUrl("https://www.netbk.co.jp/contents/pages/wpl010101/i010101CT/DI01010210");


            //　HTMLタグ内のIdから要素取得
            //IWebElement element = _WebDriver.FindElement(By.Id("loginForm"));

            //　取得した要素のうちnameを指定してログインIDとPASSWORを入力      
            // 入力
            var userElement = _WebDriver.FindElement(By.Name("userNameNewLogin"));
            userElement.SendKeys(LOGIN_ID);
            var passElement = _WebDriver.FindElement(By.Id("loginPwdSet"));
            passElement.SendKeys(PASSWORD);
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
                System.Windows.Forms.Application.DoEvents(); 
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

            //URLにアクセスhttps://www1.mbrace.or.jp/od2/B/dindex.html
            _WebDriver.Navigate().GoToUrl("https://www.e-stat.go.jp/municipalities/cities/areacode");

            IWebElement selectElement = _WebDriver.FindElement(By.Name("date_year"));
            //チェックボックス、ラジオボタン
            //_WebDriver.FindElement(By.XPath("/html/body/center/form/table/tbody/tr[1]/td[3]/select/option[2]")).Click();
            var selectObject = new SelectElement(selectElement);

            // Select an <option> based upon its text
            selectObject.SelectByText("2019年");

        }
    }
}
