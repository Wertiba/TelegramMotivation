SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE words_in_word.items;
TRUNCATE TABLE words_in_word.words_in_game;
TRUNCATE TABLE words_in_word.participants;
TRUNCATE TABLE words_in_word.games;
TRUNCATE TABLE words_in_word.votes;

SET FOREIGN_KEY_CHECKS = 1;