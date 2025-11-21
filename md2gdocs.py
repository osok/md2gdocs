#!/usr/bin/env python3
"""
Convert Markdown with Mermaid diagrams to Google Docs.

This script parses markdown files, renders mermaid diagrams as images,
and creates a Google Doc with the content and embedded diagram images.

Requirements:
    pip install google-auth google-auth-oauthlib google-auth-httplib2
    pip install google-api-python-client
    pip install markdown
    pip install Pillow
    pip install requests
    
    Also requires either:
    - A local mermaid CLI installation (npm install -g @mermaid-js/mermaid-cli)
    - Or uses the mermaid.ink API for rendering
"""

import os
import re
import json
import base64
import tempfile
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import io

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

# Markdown parsing
import markdown
from markdown.extensions import fenced_code

# Image handling
from PIL import Image
import requests

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]


class MermaidRenderer:
    """Handle rendering of Mermaid diagrams to images."""
    
    def __init__(self, use_api: bool = True):
        """
        Initialize the renderer.
        
        Args:
            use_api: If True, use mermaid.ink API. If False, use local mermaid CLI.
        """
        self.use_api = use_api
        if not use_api:
            # Check if mermaid CLI is installed
            try:
                subprocess.run(['mmdc', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Warning: mermaid CLI not found. Falling back to API.")
                self.use_api = True
    
    def render_to_image(self, mermaid_code: str, output_path: str) -> bool:
        """
        Render mermaid code to an image file.
        
        Args:
            mermaid_code: The mermaid diagram code
            output_path: Path where the image should be saved
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_api:
            return self._render_with_api(mermaid_code, output_path)
        else:
            return self._render_with_cli(mermaid_code, output_path)
    
    def _render_with_api(self, mermaid_code: str, output_path: str) -> bool:
        """Render using mermaid.ink API."""
        try:
            # Encode the mermaid code for the API
            encoded = base64.urlsafe_b64encode(
                mermaid_code.encode('utf-8')
            ).decode('ascii')
            
            # Request the image from mermaid.ink
            url = f"https://mermaid.ink/img/{encoded}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the image
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"Error rendering mermaid diagram with API: {e}")
            return False
    
    def _render_with_cli(self, mermaid_code: str, output_path: str) -> bool:
        """Render using local mermaid CLI."""
        try:
            # Create temporary file with mermaid code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_code)
                temp_mmd = f.name
            
            # Run mermaid CLI
            subprocess.run([
                'mmdc',
                '-i', temp_mmd,
                '-o', output_path,
                '-t', 'default',
                '-b', 'white'
            ], check=True, capture_output=True)
            
            # Clean up
            os.unlink(temp_mmd)
            return True
        except Exception as e:
            print(f"Error rendering mermaid diagram with CLI: {e}")
            if os.path.exists(temp_mmd):
                os.unlink(temp_mmd)
            return False


class MarkdownToGoogleDocs:
    """Convert Markdown with Mermaid diagrams to Google Docs."""
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize the converter.
        
        Args:
            credentials_file: Path to Google API credentials JSON file
        """
        self.creds = None
        self.credentials_file = credentials_file
        self.mermaid_renderer = MermaidRenderer(use_api=True)
        self.temp_images = []
        
    def authenticate(self):
        """Authenticate with Google APIs."""
        token_file = 'token.json'
        
        # Load existing token
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())
    
    def parse_markdown(self, markdown_text: str) -> Tuple[List[Dict], List[str]]:
        """
        Parse markdown and extract mermaid diagrams.
        
        Args:
            markdown_text: The markdown content
            
        Returns:
            Tuple of (content blocks, mermaid codes)
        """
        blocks = []
        mermaid_diagrams = []
        
        # Split by code blocks
        parts = re.split(r'```(\w+)?\n(.*?)```', markdown_text, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            if i % 3 == 0:  # Regular markdown content
                if part.strip():
                    blocks.append({'type': 'markdown', 'content': part})
            elif i % 3 == 1:  # Code block language
                lang = part
            else:  # Code block content
                if lang and lang.lower() == 'mermaid':
                    mermaid_diagrams.append(part)
                    blocks.append({'type': 'mermaid', 'index': len(mermaid_diagrams) - 1})
                else:
                    # Other code blocks
                    blocks.append({'type': 'code', 'language': lang or '', 'content': part})
        
        return blocks, mermaid_diagrams
    
    def upload_image_to_drive(self, image_path: str, drive_service) -> str:
        """
        Upload an image to Google Drive and get its ID.
        
        Args:
            image_path: Path to the image file
            drive_service: Google Drive API service instance
            
        Returns:
            The Drive file ID
        """
        file_metadata = {
            'name': os.path.basename(image_path),
            'mimeType': 'image/png'
        }
        
        with open(image_path, 'rb') as f:
            media = MediaIoBaseUpload(
                io.BytesIO(f.read()),
                mimetype='image/png',
                resumable=True
            )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        # Make the file publicly accessible (optional)
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return file.get('id')
    
    def create_google_doc(self, title: str, blocks: List[Dict], 
                         mermaid_images: List[str]) -> str:
        """
        Create a Google Doc with the parsed content.
        
        Args:
            title: Document title
            blocks: Content blocks from parsing
            mermaid_images: Paths to rendered mermaid images
            
        Returns:
            The document ID
        """
        # Build services
        docs_service = build('docs', 'v1', credentials=self.creds)
        drive_service = build('drive', 'v3', credentials=self.creds)
        
        # Create a new document
        doc = docs_service.documents().create(
            body={'title': title}
        ).execute()
        
        doc_id = doc.get('documentId')
        print(f"Created document with ID: {doc_id}")
        
        # Build requests for updating the document
        # All requests will insert at index 1, and we'll reverse them
        # so they appear in the correct order
        requests = []

        for block in blocks:
            if block['type'] == 'markdown':
                # Convert markdown to plain text with basic formatting
                text = self._markdown_to_text(block['content'])
                requests.append({
                    'insertText': {
                        'location': {'index': 1},
                        'text': text + '\n'
                    }
                })

            elif block['type'] == 'code':
                # Insert code block with professional formatting
                code_text = f"\n{block['content']}\n"

                # 1. Insert the code text (without backticks)
                requests.append({
                    'insertText': {
                        'location': {'index': 1},
                        'text': code_text
                    }
                })

                # 2. Apply text formatting (monospace font + background)
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': 1 + len(code_text)
                        },
                        'textStyle': {
                            'weightedFontFamily': {
                                'fontFamily': 'Courier New'
                            },
                            'fontSize': {
                                'magnitude': 10,
                                'unit': 'PT'
                            },
                            'backgroundColor': {
                                'color': {
                                    'rgbColor': {
                                        'red': 0.95,
                                        'green': 0.95,
                                        'blue': 0.95
                                    }
                                }
                            }
                        },
                        'fields': 'weightedFontFamily,fontSize,backgroundColor'
                    }
                })

                # 3. Apply paragraph formatting (left border for visual distinction)
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': 1 + len(code_text)
                        },
                        'paragraphStyle': {
                            'borderLeft': {
                                'color': {
                                    'color': {
                                        'rgbColor': {
                                            'red': 0.6,
                                            'green': 0.6,
                                            'blue': 0.6
                                        }
                                    }
                                },
                                'width': {
                                    'magnitude': 3.0,
                                    'unit': 'PT'
                                },
                                'padding': {
                                    'magnitude': 10.0,
                                    'unit': 'PT'
                                },
                                'dashStyle': 'SOLID'
                            }
                        },
                        'fields': 'borderLeft'
                    }
                })

            elif block['type'] == 'mermaid':
                # Insert mermaid diagram image
                image_path = mermaid_images[block['index']]
                if os.path.exists(image_path):
                    # Upload image to Drive
                    image_id = self.upload_image_to_drive(image_path, drive_service)

                    # Insert image into document
                    requests.append({
                        'insertInlineImage': {
                            'location': {'index': 1},
                            'uri': f"https://drive.google.com/uc?id={image_id}",
                            'objectSize': {
                                'height': {'magnitude': 300, 'unit': 'PT'},
                                'width': {'magnitude': 400, 'unit': 'PT'}
                            }
                        }
                    })

                    # Add spacing after image
                    requests.append({
                        'insertText': {
                            'location': {'index': 1},
                            'text': '\n\n'
                        }
                    })
        
        # Execute all requests
        if requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests[::-1]}  # Reverse to maintain indices
            ).execute()
        
        return doc_id
    
    def _markdown_to_text(self, markdown_text: str) -> str:
        """
        Convert markdown to plain text with basic formatting.
        
        Args:
            markdown_text: Markdown content
            
        Returns:
            Plain text version
        """
        # Simple conversion - you can enhance this
        text = markdown_text
        
        # Convert headers
        text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
        
        # Convert bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Convert italic
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Convert links
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1 (\2)', text)
        
        # Convert lists
        text = re.sub(r'^\*\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\-\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        return text
    
    def convert(self, markdown_file: str, doc_title: Optional[str] = None) -> str:
        """
        Convert a markdown file to Google Docs.
        
        Args:
            markdown_file: Path to the markdown file
            doc_title: Optional title for the Google Doc
            
        Returns:
            The Google Doc ID
        """
        # Authenticate
        self.authenticate()
        
        # Read markdown file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Parse markdown and extract mermaid diagrams
        blocks, mermaid_codes = self.parse_markdown(markdown_content)
        
        # Render mermaid diagrams
        mermaid_images = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, mermaid_code in enumerate(mermaid_codes):
                image_path = os.path.join(temp_dir, f'mermaid_{i}.png')
                if self.mermaid_renderer.render_to_image(mermaid_code, image_path):
                    mermaid_images.append(image_path)
                else:
                    mermaid_images.append('')
            
            # Create Google Doc
            if not doc_title:
                doc_title = Path(markdown_file).stem
            
            doc_id = self.create_google_doc(doc_title, blocks, mermaid_images)
        
        # Generate URL
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        print(f"\nDocument created successfully!")
        print(f"URL: {doc_url}")
        
        return doc_id


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert Markdown with Mermaid diagrams to Google Docs'
    )
    parser.add_argument(
        'markdown_file',
        help='Path to the markdown file to convert'
    )
    parser.add_argument(
        '--title',
        help='Title for the Google Doc (default: filename without extension)'
    )
    parser.add_argument(
        '--credentials',
        default='credentials.json',
        help='Path to Google API credentials file (default: credentials.json)'
    )
    parser.add_argument(
        '--use-cli',
        action='store_true',
        help='Use local mermaid CLI instead of API for rendering'
    )
    
    args = parser.parse_args()
    
    # Check if markdown file exists
    if not os.path.exists(args.markdown_file):
        print(f"Error: File '{args.markdown_file}' not found")
        return 1
    
    # Create converter
    converter = MarkdownToGoogleDocs(credentials_file=args.credentials)
    
    # Set rendering method
    if args.use_cli:
        converter.mermaid_renderer = MermaidRenderer(use_api=False)
    
    try:
        # Convert the file
        converter.convert(args.markdown_file, args.title)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())