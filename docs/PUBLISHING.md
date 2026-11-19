# Publishing this prerelease on GitHub

Proposed repository: `calcification/cave-ps2-240p` (companion to `calcification/psikyo-ps2-240p`). **This package does not create that repository on your account.**

1. On GitHub, create a new repository named **`cave-ps2-240p`**. Do not initialize it with a README or license; both are in this package.
2. Unzip the downloadable package to get the `cave-ps2-240p` folder.
3. On macOS or Linux, open Terminal in the extracted folder and run (replace the first path if needed):

   ```bash
   cd ~/Downloads/cave-ps2-240p
   git init
   git add .
   git commit -m "Initial Cave/Taito PS2 240p beta"
   git branch -M main
   git remote add origin https://github.com/calcification/cave-ps2-240p.git
   git push -u origin main
   git tag v0.1.0-beta.1
   git push origin v0.1.0-beta.1
   ```

   On Windows, use PowerShell or Git Bash instead; change into the extracted folder using `cd "$HOME\Downloads\cave-ps2-240p"` in PowerShell, then use the same `git` commands from `git init` onward. Install [Git for Windows](https://git-scm.com/downloads/win) if `git` is not recognized.

4. Open GitHub's **Releases → Draft a new release**, select tag `v0.1.0-beta.1`, and mark **Set as a pre-release**.
5. Use the notes in [CHANGELOG.md](../CHANGELOG.md). Optionally attach the source ZIP; GitHub also generates its own source archives.
6. Confirm that **no ISOs, original game executables, GS captures, or licensed game data** have been committed.

If a remote repository already exists or you have GitHub Desktop configured, use that publishing workflow instead of running `git remote add` again.
