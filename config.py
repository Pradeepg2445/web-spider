RUN_INDEXER = True
SKIP_COMPLETED_TABLES = True
INDEXER_CHECK_TIME = 800 # IN SECONDS


DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_USERNAME = "root"
DB_PASSWORD = ""

DB_GENERAL = "general_data"
DB_INDEXED_KEYWORD = "indexed_keywords" 
DB_INDEXED_PAGE = "indexed_pages" 


console_colors = {
    'default': '\033[0m',  # default color (usually white)
    'red': '\033[91m',      # red
    'green': '\033[92m',    # green
    'yellow': '\033[93m',   # yellow
    'blue': '\033[94m',     # blue
    'magenta': '\033[95m',  # magenta
    'cyan': '\033[96m'      # cyan
}


fileExtensions = (
   "doc", "docx", "pdf", "rtf", # Document files
  "jpg", "jpeg", "png", "gif", "bmp", # Image files
  "tiff", "eps", "ai", "psd", # Image files (continued)
  "mp3", "wav", "ogg", "flac", "aac", # Audio files
  "wma", "m4a", "mid", "midi", # Audio files (continued)
  "mp4", "avi", "mkv", "mov", "wmv", # Video files
  "flv", "mpeg", "3gp", "webm", "vob", # Video files (continued)
  "zip", "rar", "7z", "tar", "gz", # Compressed files
  "xz", "bz2", "tgz", # Compressed files (continued)
  "xls", "xlsx", "csv", "ods", # Spreadsheet files
  "xlsm", "numbers", # Spreadsheet files (continued)
  "ppt", "pptx", "key", # Presentation files
  "odp", "pps", # Presentation files (continued)
  "exe", "dmg", "deb", "rpm", "bat", # Executable files
  "sh", "jar", "com", "msi", # Executable files (continued)
  "json", "xml", "yaml", "ini", "cfg", # Configuration files
  "properties", "plist", "yml", # Configuration files (continued)
  "iso", "img", "vhd", "vmdk", # Disk image files
  "sql", "db", "mdb", "accdb", # Database files
  "java", "py", "cpp", "c", "cs", "vb", # Source code files
  "h", "hpp", "rb", "pl", "lua", "swift", # Source code files (continued)
  "go", "ts", "jsx", "tsx", # Source code files (continued)  
  "svg", # Vector graphic files
  "wpd", # Text files (continued)
  "ots", # Spreadsheet files
  "otp", # Presentation files
  "accdb", "frm", # Database files
  "class", "groovy", # Java files
  "jspx", "do", # Java files (continued)
  "pyc", "pyd", "pyo", # Python files
  "pyw", "pyz", "pywz", # Python files (continued)
  "sln", "vcxproj", # C# files 
  "dtd", "conf", "htaccess", "htpasswd", # Configuration files
  "changelog", "bak", # Log files
  "swp", "temp", # Temporary files
  "thumbs.db", ".DS_Store", # System files
  "torrent", "sfv", "nfo", # Other files
  "cue", "url", "webloc", "desktop", # Other files (continued)
  "lnk", "manifest", # Other files (continued)
  "toast", "cdr", "mdf", # Disk image files
  "nrg", "pdb", # Disk image files (continued)
  "bin", "mds", # Disk image files (continued)
  "z", "pkg", "app", "xpi", "crx", # Package files
  "ipa", # Package files (continued)
  "epub", "mobi", "azw", "azw3", "lit", # E-book files
  "vcf", "ldif" # Contact files (continued)
)