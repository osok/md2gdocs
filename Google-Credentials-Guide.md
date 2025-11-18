# Detailed Google API Credentials Setup Guide

## Step-by-Step Instructions with Screenshots References

### Step 1: Access Google Cloud Console

1. Open your browser and go to: https://console.cloud.google.com/
2. Sign in with your Google account (the same one you want to create docs with)

### Step 2: Create a New Project (or Select Existing)

1. Look at the top navigation bar for the project dropdown (next to "Google Cloud")
2. Click the dropdown and then click **"NEW PROJECT"**
3. Enter details:
   - **Project name**: Something like "Markdown-to-Docs-Converter"
   - **Organization**: Leave as-is (usually "No organization")
4. Click **"CREATE"**
5. Wait about 30 seconds for the project to be created

### Step 3: Enable Required APIs

#### Enable Google Docs API:
1. In the left sidebar, click **"APIs & Services"** → **"Library"**
   - If you don't see the sidebar, click the ☰ hamburger menu in the top-left
2. In the search box, type **"Google Docs API"**
3. Click on **"Google Docs API"** in the results
4. Click the blue **"ENABLE"** button
5. Wait for it to enable (about 10-15 seconds)

#### Enable Google Drive API:
1. Click back to the API Library (or use browser back button)
2. In the search box, type **"Google Drive API"**
3. Click on **"Google Drive API"** in the results
4. Click the blue **"ENABLE"** button
5. Wait for it to enable

### Step 4: Create OAuth 2.0 Credentials

1. In the left sidebar, click **"APIs & Services"** → **"Credentials"**

2. Before creating credentials, you might need to configure the consent screen:
   - If you see a warning about configuring consent screen, click **"CONFIGURE CONSENT SCREEN"**
   - If not, skip to step 3

#### Configure OAuth Consent Screen (if required):
1. Choose **"External"** (unless you have a Google Workspace account, then choose "Internal")
2. Click **"CREATE"**
3. Fill in the required fields:
   - **App name**: "Markdown to Docs Converter" (or any name you prefer)
   - **User support email**: Select your email from the dropdown
   - **Developer contact information**: Enter your email address
4. Click **"SAVE AND CONTINUE"**
5. On the "Scopes" page, click **"SAVE AND CONTINUE"** (we'll add scopes automatically later)
6. On the "Test users" page, click **"ADD USERS"**
   - Add your own email address
   - Click **"ADD"**
7. Click **"SAVE AND CONTINUE"**
8. Review and click **"BACK TO DASHBOARD"**

#### Create the Credentials:
1. Go back to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Choose **"OAuth client ID"**
4. For "Application type", select **"Desktop app"**
5. For "Name", enter something like "Python Script Client"
6. Click **"CREATE"**

### Step 5: Download the Credentials

1. A popup will appear showing your client ID and client secret
2. Click **"DOWNLOAD JSON"** button
3. **IMPORTANT**: Rename the downloaded file to exactly: `credentials.json`
4. Move this file to the same folder where you saved the Python script

### Step 6: Verify Your Setup

Your folder should now contain:
```
your-project-folder/
├── markdown_to_gdocs.py
├── credentials.json     <-- The file you just downloaded
├── requirements.txt
├── example.md
└── README.md
```

## First-Time Authentication

When you run the script for the first time:

1. Your browser will automatically open
2. You might see a warning "Google hasn't verified this app"
   - Click **"Advanced"**
   - Click **"Go to [Your App Name] (unsafe)"** - This is safe since it's your own app
3. Review the permissions:
   - View and manage your Google Docs
   - View and manage your Google Drive files
4. Click **"Allow"**
5. You'll see "The authentication flow has completed"
6. The script will save a `token.json` file so you won't need to authenticate again

## Common Issues and Solutions

### "Access blocked: This app's request is invalid"
- Make sure you configured the OAuth consent screen first
- Check that you selected "Desktop app" not "Web application"

### "Error 400: redirect_uri_mismatch"
- You probably selected "Web application" instead of "Desktop app"
- Go back and create a new OAuth client ID with "Desktop app" selected

### "Error 403: Access Denied"
- You might be signed into multiple Google accounts
- Try using an incognito/private browser window
- Make sure you added your email as a test user in the OAuth consent screen

### "Google hasn't verified this app" warning
- This is normal for personal projects
- It's safe to proceed since you created the app yourself
- Click "Advanced" → "Go to [app] (unsafe)"

### Can't find APIs & Services
- Make sure you're in the Google Cloud Console: https://console.cloud.google.com/
- Not in regular Google Drive or Docs
- Check that you have a project selected in the top dropdown

### "API has not been used in project" error
- Go back to APIs & Services → Library
- Make sure both Google Docs API and Google Drive API show as "ENABLED"
- If they show "ENABLE" button, click it to enable them

## Testing Your Setup

Once you have `credentials.json` in place, test with:

```bash
# Install dependencies first
pip install -r requirements.txt

# Run the script with the example file
python markdown_to_gdocs.py example.md --title "Test Document"
```

The script should:
1. Open your browser for authentication (first time only)
2. Create a new Google Doc
3. Display the URL to your new document

## Security Notes

- **Keep `credentials.json` private** - Don't share it or commit it to Git
- **Keep `token.json` private** - Created after first run, also contains sensitive data
- Add both files to `.gitignore` if using Git:
  ```
  credentials.json
  token.json
  ```

## Need More Help?

- Google's Official Guide: https://developers.google.com/docs/api/quickstart/python
- Google Cloud Console: https://console.cloud.google.com/
- API Library: https://console.cloud.google.com/apis/library