using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CaptureImage
{
    class Test
    {
        static void Main(string[] args)
        {
            test();
        }

        static void test()
        {
            //Renci.SshNet.ConnectionInfo c = new Renci.SshNet.ConnectionInfo("10.1.1.103", "qa", new Renci.SshNet.PasswordAuthenticationMethod("qa", "qa"));
            Renci.SshNet.SshClient c = new Renci.SshNet.SshClient("10.1.1.103", "qa", "qa");
            try
            {
                c.Connect();
                Renci.SshNet.SshCommand cmd = c.RunCommand("ls -l");

                MemoryStream m1 = new MemoryStream();
                MemoryStream m2 = new MemoryStream();
                MemoryStream m3 = new MemoryStream();

                Renci.SshNet.Shell s = c.CreateShell(m1, m2, m3);
                s.Start();

                System.Threading.Thread.Sleep(3000);

                s.Stop();


            }
            catch (Exception) { }
            finally
            {
                try { c.Disconnect(); }
                catch (Exception) { }
            }

        }

    }
}
