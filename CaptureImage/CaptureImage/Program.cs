using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace CaptureImage
{
    class Program
    {
        static void logIt(string msg)
        {
            System.Diagnostics.Trace.WriteLine(msg);
        }
        static void usage()
        {
            System.Console.Out.Write("");
        }
        static void Main(string[] args)
        {
            System.Configuration.Install.InstallContext _args = new System.Configuration.Install.InstallContext(null, args);
            if (_args.IsParameterTrue("debug"))
            {
                System.Console.Out.WriteLine("Wait for debugger, press any key to continue...");
                System.Console.ReadKey();
            }
            if (!_args.Parameters.ContainsKey("dir"))
            {
                _args.Parameters.Add("dir", System.Environment.CurrentDirectory);
            }
            if(!_args.Parameters.ContainsKey("imei"))
                _args.Parameters.Add("imei", "output");
            if (!_args.Parameters.ContainsKey("ip"))
                _args.Parameters.Add("ip", "10.1.1.103");
            try
            {
                string s = System.IO.Path.Combine(_args.Parameters["dir"], _args.Parameters["imei"]);
                try
                {
                    System.IO.Directory.Delete(s, true);
                }
                catch (Exception) { }
                System.IO.Directory.CreateDirectory(s);
                _args.Parameters.Add("target", s);
            }
            catch (Exception) { }

            if(_args.Parameters.ContainsKey("target") && System.IO.Directory.Exists(_args.Parameters["target"]))
            {
                // start
                //test(_args.Parameters);
                //downloadThread();
                //test2();
                download_test();
            }
            else
            {
                //test();
            }
        }

        static void start(string target)
        {

        }
        static void test(System.Collections.Specialized.StringDictionary args)
        {
            //Renci.SshNet.ConnectionInfo c = new Renci.SshNet.ConnectionInfo("10.1.1.103", "qa", new Renci.SshNet.PasswordAuthenticationMethod("qa", "qa"));
            Renci.SshNet.SshClient c = new Renci.SshNet.SshClient(args["ip"], "qa", "qa");
            c.Connect();

            string[] ports = getCameras(c);

            //Renci.SshNet.ShellStream ss = c.CreateShellStream("test", 80, 32, 800, 600, 1024);
            //ss.WriteLine("ls -l");
            //List<string> response = new List<string>();
            //string line = null;
            //do
            //{
            //    line = ss.ReadLine(new TimeSpan(10000));
            //    if (line != null)
            //        response.Add(line);

            //} while (line != null);
            //logIt(string.Join(System.Environment.NewLine, response));

            //response.Clear();
            //ss.WriteLine("gphoto2 --list-ports");
            //do
            //{
            //    line = ss.ReadLine(new TimeSpan(10000));
            //    if (line != null)
            //        response.Add(line);

            //} while (line != null);
            //logIt(string.Join(System.Environment.NewLine, response));

            //ss.Close();
            c.Disconnect();
        }
        static void download_test()
        {
            Renci.SshNet.SftpClient sftp = new Renci.SshNet.SftpClient("10.1.1.103", "qa", "qa");
            sftp.Connect();
            string pwd = sftp.WorkingDirectory;
            var files = sftp.ListDirectory(".");
            sftp.Disconnect();

            Renci.SshNet.ScpClient scp = new Renci.SshNet.ScpClient("10.1.1.103", "qa", "qa");
            scp.Connect();
            using (var ms = new MemoryStream())
            {
                scp.Download("1.jpg", ms);
                System.IO.File.WriteAllBytes("1.jpg", ms.ToArray());
            }
            scp.Disconnect();
        }

        static void test2()
        {
            string s1 = @"Model                          Port            
----------------------------------------------------------
Sony Alpha-A6000 (Control)     usb:001,010     
Sony Alpha-A6000 (Control)     usb:001,011     
Sony Alpha-A6000 (Control)     usb:001,012     
";

            Regex r = new Regex(@"\s*(Sony.+)\s+(usb.+)\s*");
            var m = r.Matches(s1);

        }

        static string[] getCameras(Renci.SshNet.SshClient ssh)
        {
            logIt("getCameras: ++");
            List<string> ports = new List<string>();
            Renci.SshNet.SshCommand cmd = ssh.RunCommand("gphoto2 --auto-detect");
            if(cmd.ExitStatus == 0)
            {
                logIt(cmd.Result);
                Regex r = new Regex(@"\s*(Sony.+)\s+(usb.+)\s*");
                //var matches = r.Matches(cmd.Result);
                foreach(Match m in r.Matches(cmd.Result))
                {
                    if(m.Success && m.Groups.Count > 2)
                    {
                        string name = m.Groups[1].Value.Trim();
                        string id = m.Groups[2].Value.Trim();
                        ports.Add(id);
                    }
                }
            }
            logIt("getCameras: --");
            return ports.ToArray();
        }
        static Dictionary<string,string> getCameraProperties(Renci.SshNet.SshClient ssh, string cameraPort)
        {
            Dictionary<string, string> ret = new Dictionary<string, string>();
            logIt($"getCameraProperties: ++ port={cameraPort}");
            Renci.SshNet.SshCommand cmd = ssh.RunCommand($"gphoto2 --summary --ports={cameraPort}");
            if (cmd.ExitStatus == 0)
            {

            }
            logIt("getCameraProperties: --");
            return ret;
        }
    }
}
