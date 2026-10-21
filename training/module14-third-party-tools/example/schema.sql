-- Run in an approved development project, after replacing YOUR_PROJECT_ID.
-- Create the sentinel dataset in the chosen region before executing this SQL.
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.sentinel.company_profiles` (
  company_id STRING NOT NULL,
  company_name STRING NOT NULL,
  summary STRING NOT NULL,
  source_uri STRING NOT NULL,
  reviewed_on DATE NOT NULL,
  approved BOOL NOT NULL
)
CLUSTER BY company_id;

-- Deliberately fictional fixture. This is not evidence about a real company.
-- Execute this insert once; repeating it adds another row.
INSERT INTO `YOUR_PROJECT_ID.sentinel.company_profiles`
  (company_id, company_name, summary, source_uri, reviewed_on, approved)
VALUES (
  'ACME-001',
  'Acme Robotics (fictional training company)',
  'Fictional training profile: founded in 2012; manufactures warehouse robots.',
  'training-fixture:ACME-001',
  CURRENT_DATE(),
  TRUE
);
