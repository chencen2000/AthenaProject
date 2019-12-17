using System;
using System.Collections.Generic;
using System.Configuration;
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
                test2();
                //download_test();
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
            try
            {
                c.Connect();

                string[] ports = getCameras(c);
                Dictionary<string, object> cameras = new Dictionary<string, object>();
                foreach (string p in ports)
                {
                    Dictionary<string, string> prop = getCameraProperties(c, p);
                    cameras.Add(p, prop);
                    // look for camera id
                }

                // take photo
                foreach (KeyValuePair<string, object> kvp in cameras)
                {
                    Renci.SshNet.SshCommand cmd = c.RunCommand($"gphoto2 --port={kvp.Key} --capture-image-and-download --filename=1.jpg --force-overwrite");
                }
            }
            catch (Exception) { }
            finally
            {
                try { c.Disconnect(); }
                catch (Exception) { }
            }
            
        }
        static string lookForCamera(Dictionary<string,string> prop)
        {
            string ret = "";

            return ret;
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
            var appSettings = ConfigurationManager.AppSettings;
            
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
            Renci.SshNet.SshCommand cmd = ssh.RunCommand($"gphoto2 --summary --port={cameraPort}");
            if (cmd.ExitStatus == 0)
            {
                Regex r = new Regex(@"Manufacturer: (.+)[\s+]Model: (.+)\s+Version: (.+)\s+Serial Number: (\d+)");
                Match m = r.Match(cmd.Result);
                if (m.Success && m.Groups.Count>4)
                {
                    ret["maker"] = m.Groups[1].Value.Trim();
                    ret["model"] = m.Groups[2].Value.Trim();
                    ret["version"] = m.Groups[3].Value.Trim();
                    ret["serialnumber"] = m.Groups[4].Value.Trim();
                }
            }
            logIt("getCameraProperties: --");
            return ret;
        }
    }
}
