########################################
# MySQL Crash Course
# http://www.forta.com/books/0672327120/
# Example table population scripts
########################################


##########################
# Populate units table
##########################
INSERT IGNORE INTO units(keyword, unit)
VALUES('teaspoon','teaspoon'), ('teaspoons','teaspoon'),('tsp', 'teaspoon'), ('tsps', 'teaspoon');
INSERT IGNORE INTO units(keyword, unit)
VALUES('tablespoon','tablespoon'), ('tablespoons','tsp'),('tblspoon', 'tablespoon'),('tbl', 'tablespoon'), ('tbsp', 'tablespoon');
INSERT IGNORE INTO units(keyword, unit)
VALUES('cup','cup'),('cups','cup'),('c','cup'), ('cup(s)', 'cup');
INSERT IGNORE INTO units(keyword, unit)
VALUES('lb','lb'),('lbs','lb'),('lb(s)','lb'),('pound','lb', 'pounds','lb');
INSERT IGNORE INTO units(keyword, unit)
VALUES('g','g'),('gs','g'),('gram','g'),('grams','g');
INSERT IGNORE INTO units(keyword, unit)
VALUES('ml','ml'),('mls','ml');
INSERT IGNORE INTO units(keyword, unit)
VALUES('oz','oz'),('ozs','oz'),('ounce','oz'), ('ounces', 'oz');
INSERT IGNORE INTO units(keyword, unit)
VALUES('pinch','pinch'),('pinch of','pinch'), ('dash', 'pinch'), ('dash of', 'pinch');
INSERT IGNORE INTO units(keyword, unit)
VALUES('whole','unit'),('small','unit'),('medium','unit'),('large','unit');

