import pandas as pd
import logging

class SGAReader:
    """Read SGA CSV files with proper encoding and separator"""
    
    def read(self, file_path: str) -> pd.DataFrame:
        """Read SGA CSV file"""
        try:
            # Try UTF-8 first, then Latin-1
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(
                        file_path,
                        sep=';',
                        quotechar='"',
                        encoding=encoding,
                        dtype=str
                    )
                    logging.info(f'Read {len(df)} records from {file_path} (encoding: {encoding})')
                    return df
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f'Could not read {file_path} with available encodings')
        except Exception as e:
            logging.error(f'Error reading {file_path}: {e}')
            raise
