Parsing Logic





No external AI/ML models were used for parsing



Regex patterns were manually crafted for:





Invoice #: Invoice #:\s*(\w+)|Invoice Number:\s*(\w+)



Date: Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})



Vendor: From:\s*(.+)|Vendor:\s*(.+)



Total: Total:\s*\$?(\d+\.?\d*)



Line Items: (\d+)\s+([^\d\n]+)\s+\$?(\d+\.?\d*)



No prompts were used as parsing is regex-based
