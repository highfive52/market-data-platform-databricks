CREATE TABLE workspace.market_data.delta_lake_lab (
    id INT,
    message STRING
)
USING DELTA;

INSERT INTO workspace.market_data.delta_lake_lab
VALUES
    (1, 'First Delta transaction'),
    (2, 'Second Delta transaction');
