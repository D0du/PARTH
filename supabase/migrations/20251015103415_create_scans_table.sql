/*
  # Create scans table for vulnerability scanner

  1. New Tables
    - `scans`
      - `id` (uuid, primary key) - Unique identifier for each scan
      - `tool` (text) - Name of the scanning tool used (nmap, nikto, nuclei)
      - `target` (text) - Target IP address or domain name
      - `result` (text) - Complete scan output and results
      - `status` (text) - Scan status (completed, failed, timeout, error)
      - `created_at` (timestamptz) - Timestamp when scan was performed
      - `user_id` (uuid) - Reference to the user who initiated the scan (nullable for now)

  2. Security
    - Enable RLS on `scans` table
    - Add policy for all users to insert scan results
    - Add policy for all users to read scan results
    
  3. Indexes
    - Create index on created_at for faster sorting
    - Create index on tool for filtering by tool type
    - Create index on target for searching by target
*/

CREATE TABLE IF NOT EXISTS scans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tool text NOT NULL,
  target text NOT NULL,
  result text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  created_at timestamptz DEFAULT now(),
  user_id uuid
);

ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all users to insert scans"
  ON scans
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow all users to read scans"
  ON scans
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_tool ON scans(tool);
CREATE INDEX IF NOT EXISTS idx_scans_target ON scans(target);
