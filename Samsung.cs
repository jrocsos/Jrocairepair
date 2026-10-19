using System;
using System.Diagnostics;
using System.IO;
using UnityEngine; // If using Unity; otherwise remove this line and use Console.WriteLine()

public class SFRPManager : MonoBehaviour
{
    private string adbPath = "adb"; // Ensure 'adb' is in your system PATH or provide full path like "C:/platform-tools/adb.exe"

    /// <summary>
    /// Initiates the Samsung FRP Bypass process.
    /// </summary>
    public void StartFrpBypass()
    {
        Debug.Log("[SFRP] Starting FRP Bypass Process...");

        // Step 1: Check if ADB is accessible
        if (!IsAdbAvailable())
        {
            Debug.LogError("[SFRP] ADB not found in PATH. Please install Platform-Tools.");
            return;
        }

        // Step 2: Execute the bypass sequence
        StartCoroutine(BypassSequence());
    }

    private bool IsAdbAvailable()
    {
        try
        {
            using (var process = new Process())
            {
                process.StartInfo.FileName = "cmd.exe";
                process.StartInfo.Arguments = "/c where adb";
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.UseShellExecute = false;
                process.Start();
                process.WaitForExit();
                return process.ExitCode == 0;
            }
        }
        catch
        {
            return false;
        }
    }

    private System.Collections.IEnumerator BypassSequence()
    {
        yield return null; // Wait for frame

        // Step 3: Enable TalkBack Accessibility
        Debug.Log("[SFRP] Enabling TalkBack...");
        RunAdbCommand("shell settings put secure enabled_accessibility_services com.google.android.marvin.talkback/com.google.android.accessibility.talkback.TalkBackService");
        RunAdbCommand("shell settings put secure accessibility_enabled 1");
        yield return new WaitForSeconds(3f);

        // Step 4: Start Shizuku Server (Assuming Shizuku APK is already installed)
        Debug.Log("[SFRP] Starting Shizuku Server...");
        RunAdbCommand("shell sh /data/local/tmp/shizuku/start.sh");
        yield return new WaitForSeconds(5f);

        // Step 5: Grant Permissions via Shizuku
        Debug.Log("[SFRP] Granting Permissions via Shizuku...");
        RunAdbCommand("shell sh /data/local/tmp/shizuku/api.sh grant");
        yield return new WaitForSeconds(2f);

        // Step 6: Delete FRP Token
        Debug.Log("[SFRP] Deleting FRP Token...");
        RunAdbCommand("shell content delete --uri content://settings/secure --where \"name='frp_status'\"");
        RunAdbCommand("shell content delete --uri content://settings/secure --where \"name='google_account_data'\"");
        
        // Clear Google Services to force re-login
        Debug.Log("[SFRP] Clearing Google Services Data...");
        RunAdbCommand("shell pm clear com.google.android.gms");
        RunAdbCommand("shell pm clear com.google.android.gsf");
        yield return new WaitForSeconds(2f);

        // Step 7: Reboot Device
        Debug.Log("[SFRP] Rebooting Device...");
        RunAdbCommand("reboot");
        
        Debug.Log("[SFRP] FRP Bypass Sequence Completed!");
    }

    private void RunAdbCommand(string command)
    {
        try
        {
            using (var process = new Process())
            {
                process.StartInfo.FileName = adbPath;
                process.StartInfo.Arguments = command;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.UseShellExecute = false;
                process.Start();
                
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();
                
                process.WaitForExit();

                if (!string.IsNullOrEmpty(error))
                {
                    Debug.LogWarning($"[ADB Error]: {error}");
                }
                else
                {
                    Debug.Log($"[ADB Success]: {command}");
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[ADB Exception]: {ex.Message}");
        }
    }
}