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
                //try
                //{
                //    System.IO.Directory.Delete(s, true);
                //}
                //catch (Exception) { }
                System.IO.Directory.CreateDirectory(s);
                _args.Parameters.Add("target", s);
            }
            catch (Exception) { }

            if(_args.Parameters.ContainsKey("target") && System.IO.Directory.Exists(_args.Parameters["target"]))
            {
                // start
                ret = start(_args.Parameters);
                //test(_args.Parameters);
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
                    if (!startProcess(ssh, cameras, args))
                        ret = 2;
                    else
                        ret = 0;
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
                Renci.SshNet.SshCommand cmd = c.RunCommand("sudo ls -l");
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
        static bool downloadFile(string targetFilename, System.Collections.Specialized.StringDictionary args)
        {
            bool ret = false;
            logIt($"downloadFile: ++ filename={targetFilename}");
            //Renci.SshNet.SftpClient sftp = new Renci.SshNet.SftpClient(args["ip"], "qa", "qa");
            //sftp.Connect();
            //string pwd = sftp.WorkingDirectory;
            //var files = sftp.ListDirectory(".");
            //sftp.Disconnect();

            Renci.SshNet.ScpClient scp = new Renci.SshNet.ScpClient(args["ip"], "qa", "qa");
            try
            {
                scp.Connect();
                using (var ms = new MemoryStream())
                {
                    scp.Download(System.IO.Path.GetFileName(targetFilename), ms);
                    System.IO.File.WriteAllBytes(targetFilename, ms.ToArray());
                    ret = true;
                }
            }
            catch (Exception ex)
            {
                logIt($"downloadFile: Exception={ex.Message}");
            }
            finally
            {
                try { scp.Disconnect(); }
                catch (Exception) { }
            }
            logIt($"downloadFile: -- ret={ret}");
            return ret;
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
            logIt("getCameraProperties: --");
            return ret;
        }
        static Dictionary<int, object> getAllCameras(Renci.SshNet.SshClient ssh)
        {
            logIt("getAllCameras: ++");
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
                    logIt($"dump camera (#{id}) properties: property count={prop.Count}");
                    foreach (KeyValuePair<string, string> kvp in prop)
                    {
                        logIt($"getCameraProperties: {kvp.Key}={kvp.Value}");
                    }
                }
                else
                {
                    // error. missing camera.
                }
            }
            logIt("getAllCameras: --");
            return cameras;
        }
        static bool controlLED(Renci.SshNet.SshClient ssh, string cmd, int delay = 0)
        {
            bool ret = false;
            Renci.SshNet.SshCommand c = ssh.RunCommand($"./LEDControl -txdata={cmd}");
            if (c.ExitStatus == 0)
            {
                ret = true;
                System.Threading.Thread.Sleep(delay);
            }
            return ret;
        }
        static bool startProcess(Renci.SshNet.SshClient ssh, Dictionary<int, object> cameras, System.Collections.Specialized.StringDictionary args)
        {
            Dictionary<string, string> camera = null;
            bool ret = false;
            string target = args["target"];
            List<Task<bool>> tasks = new List<Task<bool>>();
            Task<bool> set_exposure = null;
            int delay = 0;
            if(args.ContainsKey("delay") && Int32.TryParse(args["delay"], out delay))
            {
                logIt($"delay {delay}ms after LED on.");
                System.Console.WriteLine($"delay {delay}ms after LED on.");
            }
            controlLED(ssh, "00");
            if (cameras.ContainsKey(1))
            {
                camera = (Dictionary<string, string>)cameras[1];
                // 1. take a picture on camera 1 with low light
                // turn on light 1
                string fn = $"{camera["id"]}-2.jpg";
                //Renci.SshNet.SshCommand cmd1 = ssh.RunCommand($"./LEDControl -txdata=01");
                controlLED(ssh, "01", delay);
                Renci.SshNet.SshCommand cmd1 = ssh.RunCommand($"gphoto2 --port={camera["port"]} --set-config /main/capturesettings/exposurecompensation=19");
                Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={camera["port"]} --capture-image-and-download --filename={fn} --force-overwrite");
                var t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile(o.ToString(), args);
                    if (!r)
                        logIt($"Fail to download {o}.");
                    return r;
                }, $"{System.IO.Path.Combine(target, $"{fn}")}");
                tasks.Add(t);

                // 2. take a picture on camera 1 with high light with exposurecompensation=0
                fn = $"{camera["id"]}-1.jpg";
                //cmd1 = ssh.RunCommand($"./LEDControl -txdata=02");
                controlLED(ssh, "02", delay);
                cmd3 = ssh.RunCommand($"gphoto2 --port={camera["port"]} --capture-image-and-download --filename={fn} --force-overwrite");
                t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile(o.ToString(), args);
                    if (!r)
                        logIt($"Fail to download {o}.");
                    return r;
                }, $"{System.IO.Path.Combine(target, $"{fn}")}");
                tasks.Add(t);
                // 3. take a picture on camera 1 with high light with exposurecompensation=-3
                set_exposure = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    Renci.SshNet.SshCommand cmd = ssh.RunCommand($"gphoto2 --port={o.ToString()} --set-config /main/capturesettings/exposurecompensation=30");
                    r = cmd.ExitStatus == 0;
                    if (!r)
                        logIt($"Fail to set /main/capturesettings/exposurecompensation=34.");
                    return r;
                }, $"{camera["port"]}");
                //cmd3 = ssh.RunCommand($"gphoto2 --port={camera["port"]} --capture-image-and-download --filename={fn} --force-overwrite");
            }
            // 4. take a picture on camera 2
            if (cameras.ContainsKey(2))
            {
                camera = (Dictionary<string, string>)cameras[2];
                string fn = $"{camera["id"]}.jpg";
                //Renci.SshNet.SshCommand cmd1 = ssh.RunCommand($"./LEDControl -txdata=04");
                controlLED(ssh, "04", delay);
                Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={camera["port"]} --capture-image-and-download --filename={fn} --force-overwrite");
                var t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile(o.ToString(), args);
                    if (!r)
                        logIt($"Fail to download {o}.");
                    return r;
                }, $"{System.IO.Path.Combine(target, $"{fn}")}");
                tasks.Add(t);
            }
            // 5. take a picture on camera 3
            if (cameras.ContainsKey(3) && cameras.ContainsKey(4) && cameras.ContainsKey(5) && cameras.ContainsKey(6))
            {
                // turn on light 2+4
                //Renci.SshNet.SshCommand cmd1 = ssh.RunCommand($"./LEDControl -txdata=06");
                controlLED(ssh, "06", delay);
                Task t3 = Task<bool>.Run(() => 
                {
                    Dictionary<string, string> c3 = (Dictionary<string, string>)cameras[3];
                    Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={c3["port"]} --capture-image-and-download --filename={c3["id"]}.jpg --force-overwrite");
                    return cmd3.ExitStatus == 0;
                });
                Task t4 = Task<bool>.Run(() =>
                {
                    Dictionary<string, string> c4 = (Dictionary<string, string>)cameras[4];
                    Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={c4["port"]} --capture-image-and-download --filename={c4["id"]}.jpg --force-overwrite");
                    return cmd3.ExitStatus == 0;
                });
                Task t5 = Task<bool>.Run(() =>
                {
                    Dictionary<string, string> c5 = (Dictionary<string, string>)cameras[5];
                    Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={c5["port"]} --capture-image-and-download --filename={c5["id"]}.jpg --force-overwrite");
                    return cmd3.ExitStatus == 0;
                });
                Task t6 = Task<bool>.Run(() =>
                {
                    Dictionary<string, string> c6 = (Dictionary<string, string>)cameras[6];
                    Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={c6["port"]} --capture-image-and-download --filename={c6["id"]}.jpg --force-overwrite");
                    return cmd3.ExitStatus == 0;
                });
                Task.WaitAll(new Task[] { t3, t4, t5, t6 });
                var t = Task<bool>.Factory.StartNew((o) => 
                {
                    bool r = false;
                    r = downloadFile($"{o.ToString()}", args);
                    if (!r)
                        logIt($"Fail to download 3.jpg.");
                    return r;
                }, $"{System.IO.Path.Combine(target,"3.jpg")}");
                tasks.Add(t);
                t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile($"{o.ToString()}", args);
                    if (!r)
                        logIt($"Fail to download 4.jpg.");
                    return r;
                }, $"{System.IO.Path.Combine(target, "4.jpg")}");
                tasks.Add(t);
                t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile($"{o.ToString()}", args);
                    if (!r)
                        logIt($"Fail to download 5.jpg.");
                    return r;
                }, $"{System.IO.Path.Combine(target, "5.jpg")}");
                tasks.Add(t);
                t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile($"{o.ToString()}", args);
                    if (!r)
                        logIt($"Fail to download 6.jpg.");
                    return r;
                }, $"{System.IO.Path.Combine(target, "6.jpg")}");
                tasks.Add(t);
            }
            // 6. take a picture on camera 1 with oev=-3
            if (cameras.ContainsKey(1))
            {
                camera = (Dictionary<string, string>)cameras[1];
                // 1. take a picture on camera 1 with low light
                // turn on light 1
                string fn = $"{camera["id"]}-3.jpg";
                //Renci.SshNet.SshCommand cmd1 = ssh.RunCommand($"./LEDControl -txdata=01");
                controlLED(ssh, "01", delay);
                Renci.SshNet.SshCommand cmd3 = ssh.RunCommand($"gphoto2 --port={camera["port"]} --capture-image-and-download --filename={fn} --force-overwrite");
                var t = Task<bool>.Factory.StartNew((o) =>
                {
                    bool r = false;
                    r = downloadFile(o.ToString(), args);
                    if (!r)
                        logIt($"Fail to download {o}.");
                    return r;
                }, $"{System.IO.Path.Combine(target, $"{fn}")}");
                tasks.Add(t);
                Renci.SshNet.SshCommand cmd = ssh.RunCommand($"gphoto2 --port={camera["port"]} --set-config /main/capturesettings/exposurecompensation=19");
            }
            Task.WaitAll(tasks.ToArray());
            ret = true;
            foreach(Task<bool> t in tasks)
            {
                ret &= t.Result;
            }
            return ret;
        }
    }
}
