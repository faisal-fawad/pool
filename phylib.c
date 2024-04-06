#include "phylib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* Constructor to initialize a still ball */
phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) {
  phylib_object *new_still_ball = malloc(sizeof(phylib_object));
  if (new_still_ball == NULL) return NULL; // malloc failed

  // Creating the object
  phylib_untyped obj;
  obj.still_ball.number = number;
  obj.still_ball.pos = *pos;  

  new_still_ball->type = PHYLIB_STILL_BALL;
  new_still_ball->obj = obj;

  return new_still_ball;
}

/* Constructor to initialize a rolling ball */
phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc) {
  phylib_object *new_rolling_ball = malloc(sizeof(phylib_object));
  if (new_rolling_ball == NULL) return NULL; // malloc failed

  // Creating the object
  phylib_untyped obj;
  obj.rolling_ball.number = number;
  obj.rolling_ball.pos = *pos;
  obj.rolling_ball.vel = *vel;
  obj.rolling_ball.acc = *acc;

  new_rolling_ball->type = PHYLIB_ROLLING_BALL;
  new_rolling_ball->obj = obj;

  return new_rolling_ball;
}

/* Constructor to initialize a hole */
phylib_object *phylib_new_hole(phylib_coord *pos) {
  phylib_object *new_hole = malloc(sizeof(phylib_object));
  if (new_hole == NULL) return NULL; // malloc failed

  // Creating the object
  phylib_untyped obj;
  obj.hole.pos = *pos;

  new_hole->type = PHYLIB_HOLE;
  new_hole->obj = obj;

  return new_hole;
}

/* Constructor to initialize a horizontal cushion */
phylib_object *phylib_new_hcushion(double y) {
  phylib_object *new_hcushion = malloc(sizeof(phylib_object));
  if (new_hcushion == NULL) return NULL; // malloc failed

  // Creating the object
  phylib_untyped obj;
  obj.hcushion.y = y;

  new_hcushion->type = PHYLIB_HCUSHION;
  new_hcushion->obj = obj;

  return new_hcushion;
}

/* Constructor to initialize a vertical cushion */
phylib_object *phylib_new_vcushion(double x) { 
  phylib_object *new_vcushion = malloc(sizeof(phylib_object));
  if (new_vcushion == NULL) return NULL; // malloc failed

  // Creating the object
  phylib_untyped obj;
  obj.vcushion.x = x;

  new_vcushion->type = PHYLIB_VCUSHION;
  new_vcushion->obj = obj;
  
  return new_vcushion;
}

/* Constructor to initialize a table */
phylib_table *phylib_new_table() {
  phylib_table *new_table = malloc(sizeof(phylib_table));
  if (new_table == NULL) return NULL; // malloc failed

  new_table->time = 0.0;
  // Populating the object based on the given schema
  new_table->object[0] = phylib_new_hcushion(0);
  new_table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
  new_table->object[2] = phylib_new_vcushion(0);
  new_table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

  phylib_coord hole_positions[6] = {
    (phylib_coord){0, 0},
    (phylib_coord){0, PHYLIB_TABLE_LENGTH / 2},
    (phylib_coord){0, PHYLIB_TABLE_LENGTH},
    (phylib_coord){PHYLIB_TABLE_WIDTH, 0},
    (phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH / 2},
    (phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH}
  };

  for (int i = 4; i < PHYLIB_MAX_OBJECTS; i++) {
    if (i < 10) {
      new_table->object[i] = phylib_new_hole(&hole_positions[i - 4]);
    } else {
      new_table->object[i] = NULL;
    }
  }

  return new_table;
}

/* Copy an object from source to destination */
void phylib_copy_object(phylib_object **dest, phylib_object **src) {
  if (*src != NULL) {
    *dest = (phylib_object *)malloc(sizeof(phylib_object));
    if (*dest != NULL) memcpy(*dest, *src, sizeof(phylib_object));
  } else {
    *dest = NULL;
  }
}

/* Copy and return a table */
phylib_table *phylib_copy_table(phylib_table *table) {
  phylib_table * duplicate_table = (phylib_table *)malloc(sizeof(phylib_table));
  if (duplicate_table == NULL) return NULL; // malloc failed

  duplicate_table->time = table->time;
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    phylib_copy_object(&duplicate_table->object[i], &table->object[i]);
  }

  return duplicate_table;
}

/* Add an object to a table */
void phylib_add_object(phylib_table *table, phylib_object *object) {
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    if (table->object[i] == NULL) {
      table->object[i] = object;
      break;
    }
  }
}

/* Free the table from memory */
void phylib_free_table(phylib_table *table) {
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    if (table->object[i] != NULL) {
      free(table->object[i]);
    }
  }

  free(table);
}

/* Subtract two coordinates and return the resulting coordinate */
phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2) {
  return (phylib_coord){c1.x - c2.x, c1.y - c2.y};
}

/* Find and return the length of the coordinate from the origin */
double phylib_length(phylib_coord c) {
  return sqrt((c.x * c.x) + (c.y * c.y));
}

/* Find and return the dot product of two coordinates */
double phylib_dot_product(phylib_coord a, phylib_coord b) {
  return (a.x * b.x) + (a.y * b.y);
}

/* Find and return the distance between two objects */
double phylib_distance(phylib_object *obj1, phylib_object *obj2) {
  if (obj1->type != PHYLIB_ROLLING_BALL) return -1.0;

  switch (obj2->type) {
    case PHYLIB_ROLLING_BALL: {
      phylib_coord a = obj1->obj.rolling_ball.pos;
      phylib_coord b = obj2->obj.rolling_ball.pos;
      return sqrt(((b.x - a.x) * (b.x - a.x)) + ((b.y - a.y) * (b.y - a.y))) - PHYLIB_BALL_DIAMETER; 
    }

    case PHYLIB_STILL_BALL: {
      phylib_coord a = obj1->obj.rolling_ball.pos;
      phylib_coord b = obj2->obj.still_ball.pos;
      return sqrt(((b.x - a.x) * (b.x - a.x)) + ((b.y - a.y) * (b.y - a.y))) - PHYLIB_BALL_DIAMETER; 
    }

    case PHYLIB_HOLE: {
      phylib_coord a = obj1->obj.rolling_ball.pos;
      phylib_coord b = obj2->obj.hole.pos;
      return sqrt(((b.x - a.x) * (b.x - a.x)) + ((b.y - a.y) * (b.y - a.y))) - PHYLIB_HOLE_RADIUS;
    }

    case PHYLIB_HCUSHION: {
      double a = obj1->obj.rolling_ball.pos.y;
      double b = obj2->obj.hcushion.y;
      return fabs(b - a) - PHYLIB_BALL_RADIUS;
    }

    case PHYLIB_VCUSHION: {
      double a = obj1->obj.rolling_ball.pos.x;
      double b = obj2->obj.vcushion.x;
      return fabs(b - a) - PHYLIB_BALL_RADIUS;
    }

    default: return -1.0; // invalid type
  }
}

/* Roll a ball and return the updated values through the new pointer */
void phylib_roll(phylib_object *new, phylib_object *old, double time) {
  if (new->type == PHYLIB_ROLLING_BALL && old->type == PHYLIB_ROLLING_BALL) {
    phylib_rolling_ball o = old->obj.rolling_ball;

    new->obj.rolling_ball.pos.x = o.pos.x + (o.vel.x * time) + (.5 * o.acc.x * time * time);
    new->obj.rolling_ball.pos.y = o.pos.y + (o.vel.y * time) + (.5 * o.acc.y * time * time);

    new->obj.rolling_ball.vel.x = o.vel.x + (o.acc.x * time);
    new->obj.rolling_ball.vel.y = o.vel.y + (o.acc.y * time);

    // Check for change of sign
    if (new->obj.rolling_ball.vel.x * o.vel.x < 0) {
      new->obj.rolling_ball.vel.x = 0;
      new->obj.rolling_ball.acc.x = 0;
    }

    if (new->obj.rolling_ball.vel.y * o.vel.y < 0) {
      new->obj.rolling_ball.vel.y = 0;
      new->obj.rolling_ball.acc.y = 0;
    }
  }
}

/* Check if a rolling ball has stopped */
unsigned char phylib_stopped(phylib_object *object) {
  // We can assume the object is a rolling ball (from spec)
  if (object->type != PHYLIB_ROLLING_BALL) return 0;
  
  if (phylib_length(object->obj.rolling_ball.vel) < PHYLIB_VEL_EPSILON) {
    object->obj.still_ball = (phylib_still_ball){
      object->obj.rolling_ball.number,
      object->obj.rolling_ball.pos,
    };
    object->type = PHYLIB_STILL_BALL;
    return 1;
  }

  return 0;
}

/* Handle the collision between a rolling ball and another object */
void phylib_bounce(phylib_object **a, phylib_object **b) {
  if ((*a)->type == PHYLIB_ROLLING_BALL /* Can be assumed, but check anyways */) {
    switch ((*b)->type) {
      case PHYLIB_HCUSHION: {
        (*a)->obj.rolling_ball.vel.y = -(*a)->obj.rolling_ball.vel.y;
        (*a)->obj.rolling_ball.acc.y = -(*a)->obj.rolling_ball.acc.y;
        break;
      }
      
      case PHYLIB_VCUSHION: {
        (*a)->obj.rolling_ball.vel.x = -(*a)->obj.rolling_ball.vel.x;
        (*a)->obj.rolling_ball.acc.x = -(*a)->obj.rolling_ball.acc.x;
        break;
      }
      
      case PHYLIB_HOLE: {
        free(*a);
        *a = NULL;
        break;
      }
      
      case PHYLIB_STILL_BALL: {
        (*b)->obj.rolling_ball = (phylib_rolling_ball){
          (*b)->obj.still_ball.number,
          (*b)->obj.still_ball.pos,
          {0, 0}
        };
        (*b)->type = PHYLIB_ROLLING_BALL;
        // Flow into next case
      }

      case PHYLIB_ROLLING_BALL: {
        // Compute background information
        phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);
        phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);
        phylib_coord n = (phylib_coord){
          r_ab.x / phylib_length(r_ab),
          r_ab.y / phylib_length(r_ab)
        };
        double v_rel_n = phylib_dot_product(v_rel, n);

        // Update velocities
        (*a)->obj.rolling_ball.vel.x -= v_rel_n * n.x;
        (*a)->obj.rolling_ball.vel.y -= v_rel_n * n.y;

        (*b)->obj.rolling_ball.vel.x += v_rel_n * n.x;
        (*b)->obj.rolling_ball.vel.y += v_rel_n * n.y;

        // Adjustment for simulation
        if (phylib_length((*a)->obj.rolling_ball.vel) > PHYLIB_VEL_EPSILON) {
          (*a)->obj.rolling_ball.acc.x = -(*a)->obj.rolling_ball.vel.x / phylib_length((*a)->obj.rolling_ball.vel) * PHYLIB_DRAG;
          (*a)->obj.rolling_ball.acc.y = -(*a)->obj.rolling_ball.vel.y / phylib_length((*a)->obj.rolling_ball.vel) * PHYLIB_DRAG;
        }

        if (phylib_length((*b)->obj.rolling_ball.vel) > PHYLIB_VEL_EPSILON) {
          (*b)->obj.rolling_ball.acc.x = -(*b)->obj.rolling_ball.vel.x / phylib_length((*b)->obj.rolling_ball.vel) * PHYLIB_DRAG;
          (*b)->obj.rolling_ball.acc.y = -(*b)->obj.rolling_ball.vel.y / phylib_length((*b)->obj.rolling_ball.vel) * PHYLIB_DRAG;
        }

        break;
      }
    }
  }
}

/* Return the number of rolling balls on the table */
unsigned char phylib_rolling(phylib_table *t) {
  if (t == NULL) return 0;
  unsigned char count = 0;
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL) {
      count++; 
    }
  }
  return count;
}

/* Conduct a pool segment and return the updated table */
phylib_table *phylib_segment(phylib_table *table) {
  if (phylib_rolling(table) == 0) return NULL;
  phylib_table * copy_table = phylib_copy_table(table);

  // Prevent time from passing the max time
  for (double time = PHYLIB_SIM_RATE; time < PHYLIB_MAX_TIME; time += PHYLIB_SIM_RATE) {
    copy_table->time += PHYLIB_SIM_RATE;
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
      if (copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL) {
        phylib_roll(copy_table->object[i], table->object[i], time);
        // phylib_visualize(copy_table->object[i], copy_table->time);
      }
    }

    // Each ball must roll before attempting to return from a bounce
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
      if (copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL) {
        if (phylib_stopped(copy_table->object[i])) return copy_table; // Check if rolling ball has stopped
        for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
          if (copy_table->object[j] != NULL && copy_table->object[i] != copy_table->object[j]) {
            // Check if two objects are colliding
            if (phylib_distance(copy_table->object[i], copy_table->object[j]) < 0) {
              phylib_bounce(&copy_table->object[i], &copy_table->object[j]);
              return copy_table;
            }
          }
        }
      }
    }
  }

  return copy_table;
}

// Helper functions
char *phylib_object_string(phylib_object *object) {
  static char string[80];
  if (object==NULL) {
    snprintf(string, 80, "NULL;");
    return string;
  }
  switch (object->type) {
    case PHYLIB_STILL_BALL: {
      snprintf(string, 80,
      "STILL_BALL (%d,%6.1lf,%6.1lf)",
      object->obj.still_ball.number,
      object->obj.still_ball.pos.x,
      object->obj.still_ball.pos.y);
      break;
    }
    case PHYLIB_ROLLING_BALL: {
      snprintf(string, 80,
      "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
      object->obj.rolling_ball.number,
      object->obj.rolling_ball.pos.x,
      object->obj.rolling_ball.pos.y,
      object->obj.rolling_ball.vel.x,
      object->obj.rolling_ball.vel.y,
      object->obj.rolling_ball.acc.x,
      object->obj.rolling_ball.acc.y);
      break;
    }
    case PHYLIB_HOLE: {
      snprintf(string, 80,
      "HOLE (%6.1lf,%6.1lf)",
      object->obj.hole.pos.x,
      object->obj.hole.pos.y);
      break;
    }
    case PHYLIB_HCUSHION: {
      snprintf(string, 80,
      "HCUSHION (%6.1lf)",
      object->obj.hcushion.y);
      break;
    }
    case PHYLIB_VCUSHION: {
      snprintf(string, 80,
      "VCUSHION (%6.1lf)",
      object->obj.vcushion.x);
      break;
    }
  }
  return string;
}

void phylib_print_table(phylib_table *table) {
  if (!table) {
    printf("NULL\n");
    return;
  }

  printf("time = %6.1lf;\n", table->time);
  for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
    printf("  [%02d] = %s \n", i, phylib_object_string(table->object[i]));
  }
}
