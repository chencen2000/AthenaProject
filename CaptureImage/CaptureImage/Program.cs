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
        static int Main(string[] args)
        {
            int ret = -1;
            System.Configuration.Install.InstallContext _args = new System.Configuration.Install.InstallContext(null, args);
            if (_args.IsParameterTrue("debug"))
            {
                System.Console.Out.WriteLine("Wait for debugger, press any key to continue...");
                System.Console.ReadKey();
            }
            
            var appSettings = ConfigurationManager.AppSettings;
            if (!_args.Parameters.ContainsKey("dir"))
                _args.Parameters.Add("dir", string.IsNullOrEmpty(appSettings["dir"]) ? System.Environment.CurrentDirectory : appSettings["dir"]);
            if(!_args.Parameters.ContainsKey("imei"))
                _args.Parameters.Add("imei", string.IsNullOrEmpty(appSettings["imei"]) ? "output" : appSettings["imei"]);
            if (!_args.Parameters.ContainsKey("ip"))
                _args.Parameters.Add("ip", string.IsNullOrEmpty(appSettings["ip"]) ? "10.1.1.103" : appSettings["ip"]);
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
                ret = start(_args.Parameters);
            }
            else
            {
                //test();
            }
            return ret;
        }

        static int start(System.Collections.Specialized.StringDictionary args)
        {
            int ret = -1;
            Renci.SshNet.SshClient ssh = new Renci.SshNet.SshClient(args["ip"], "qa", "qa");
            try
            {
                ssh.Connect();
                Dictionary<int, object> cameras = getAllCameras(ssh);
                // check 1~6 camera exists
                var missing = Enumerable.Range(1, 6).Except(cameras.Keys);
                if (missing.Count() > 0)
                {
                    // missing camera.
                    System.Console.WriteLine($"Missing following camera: {string.Join(",", missing)}");
                    ret = 1;
                }
                else
                {
                    // start process
                }
            }
            catch (Exception) { }
            finally
            {
                try
                {
                    ssh.Disconnect();
                }
                catch (Exception) { }
            }
            return ret;
        }
        static void test(System.Collections.Specialized.StringDictionary args)
        {
            //Renci.SshNet.ConnectionInfo c = new Renci.SshNet.ConnectionInfo("10.1.1.103", "qa", new Renci.SshNet.PasswordAuthenticationMethod("qa", "qa"));
            Renci.SshNet.SshClient c = new Renci.SshNet.SshClient(args["ip"], "qa", "qa");
            try
            {
                c.Connect();

                string[] ports = getCameraPorts(c);
                Dictionary<string, object> cameras = new Dictionary<string, object>();
                foreach (string p in ports)
                {
                    Dictionary<string, string> prop = getCameraProperties(c, p);
                    string id = lookForCamera(prop);
                    // look for camera id
                    if (!string.IsNullOrEmpty(id))
                    {
                        prop.Add("id", id);
                        cameras.Add(p, prop);
                    }
                    else
                    {
                        // error. missing camera.
                    }
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
            var appSettings = ConfigurationManager.AppSettings;
            if (prop.ContainsKey("sn"))
            {
                ret = appSettings[prop["sn"]];
            }
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

        static string[] getCameraPorts(Renci.SshNet.SshClient ssh)
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
                    if(ret["serialnumber"].Length>7)
                        ret["sn"] = ret["serialnumber"].Substring(ret["serialnumber"].Length - 7);
                }
            }
            logIt($"getCameraProperties: dump camera properties: property count={ret.Count}");
            foreach(KeyValuePair<string,string> kvp in ret)
            {
                logIt($"getCameraProperties: {kvp.Key}={kvp.Value}");
            }
            logIt("getCameraProperties: --");
            return ret;
        }
        static Dictionary<int, object> getAllCameras(Renci.SshNet.SshClient ssh)
        {
            string[] ports = getCameraPorts(ssh);
            Dictionary<int, object> cameras = new Dictionary<int, object>();
            foreach (string p in ports)
            {
                Dictionary<string, string> prop = getCameraProperties(ssh, p);
                string id = lookForCamera(prop);
                // look for camera id
                int i = 0;
                if (!string.IsNullOrEmpty(id) && Int32.TryParse(id, out i))
                {
                    prop.Add("port", p);
                    prop.Add("id", id);
                    cameras.Add(i, prop);
                }
                else
                {
                    // error. missing camera.
                }
            }
            return cameras;
        }
        static void startProcess(Renci.SshNet.SshClient ssh, Dictionary<int, object> cameras)
        {
            Dictionary<string, string> camera = null;
            if(cameras.ContainsKey(1))
            {
                camera = (Dictionary<string, string>)cameras[1];
                // 1. take a picture on camera 1 with low light
                // 2. take a picture on camera 1 with high light with exposurecompensation=0
                // 3. take a picture on camera 1 with high light with exposurecompensation=-3

            }
            // 4. take a picture on camera 2
            if (cameras.ContainsKey(2))
            {
                camera = (Dictionary<string, string>)cameras[2];
            }
            // 5. take a picture on camera 3
            if (cameras.ContainsKey(3))
            {
                camera = (Dictionary<string, string>)cameras[3];
            }
            // 6. take a picture on camera 4
            if (cameras.ContainsKey(4))
            {
                camera = (Dictionary<string, string>)cameras[4];
            }
            // 7. take a picture on camera 5
            if (cameras.ContainsKey(5))
            {
                camera = (Dictionary<string, string>)cameras[5];
            }
            // 8. take a picture on camera 6
            if (cameras.ContainsKey(6))
            {
                camera = (Dictionary<string, string>)cameras[6];
            }
        }
    }
}
