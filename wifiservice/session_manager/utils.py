"""Utilities for session management."""
from instructions_manager.views import add_instruction_helper
from db_manager.models import get_session_collection
from status_manager.views import get_status_recent_helper
import datetime
import time
from bson.objectid import ObjectId
import asyncio
from utils.utils import check_session_active
from utils.scheduling import get_scheduler
from django.conf import settings


loop = asyncio.new_event_loop()
loop.set_debug(True)
asyncio.set_event_loop(loop)

instruction_fetch_time = 5


def get_session_obj_from_id(sess_id):
    """Get session object from id."""
    session_collection = get_session_collection()
    return session_collection.find_one({'_id': ObjectId(sess_id)})


def add_instruction(session_id, mac, code):
    """Add instruction code for mac after wait_time."""
    session = get_session_obj_from_id(session_id)
    while (session and session['stopped'] == 0):
        if add_instruction_helper(mac, code):
            break
        time.sleep(instruction_fetch_time)
        session = get_session_obj_from_id(session_id)


def stop_session_helper(sess_id):
    """Stop session with given session_id."""
    session_collection = get_session_collection()
    session = get_session_obj_from_id(sess_id)
    if session and session['stopped'] == 0:
        available_pi = get_status_recent_helper(
            settings.DEMO_CONSTANTS.demo_time)
        for pi in available_pi:
            add_instruction(sess_id, pi['mac'], 5)
        time.sleep(2 * instruction_fetch_time)
        session['stopped'] = 1
        session_collection.replace_one({'_id': ObjectId(sess_id)}, session)


def get_or_create_session(automated=False):
    """Create session and return session_id."""
    session_collection = get_session_collection()
    session = check_session_active()
    sess_id = None
    created = False
    global callbacks_list
    if not session:
        session = session_collection.insert_one(
            {'created_at': datetime.datetime.now(), 'stopped': 0,
             'automated': automated})
        sess_id = session.inserted_id
        created = True
        callbacks_list = []
    else:
        sess_id = session['_id']
    return sess_id, created


def enqueue_instructions(list_instructions, sess_id, delay):
    """Enqueue instructions in scheduler."""
    scheduler = get_scheduler()
    for instr in list_instructions:
        scheduler.enqueue_in(
            datetime.timedelta(seconds=instr[1] + delay),
            add_instruction, sess_id, instr[0], instr[2])
    scheduler.enqueue_in(
        datetime.timedelta(seconds=settings.DEMO_CONSTANTS.demo_time),
        stop_session_helper, sess_id)


def schedule_manual_mode_instructions(sess_id, available_pi, delay=0):
    """Schedule cpg ap instructions."""
    list_instructions = []
    for pi in available_pi:
        list_instructions.extend(
            [(pi['mac'], 1, 6),
             (pi['mac'], settings.DEMO_CONSTANTS.session_time, 5)])
    enqueue_instructions(list_instructions, sess_id, delay)


def schedule_automated_mode_instructions(sess_id, available_pi, delay):
    """Add to blocking_futures and executor."""
    list_instructions = []
    probe_mac = available_pi[0]['mac']
    list_instructions.extend(
        [(probe_mac, 1, 1),
         (probe_mac, settings.DEMO_CONSTANTS.probe_time, 2),
         (probe_mac, settings.DEMO_CONSTANTS.probe_time + 20, 6),
         (probe_mac, settings.DEMO_CONSTANTS.session_time, 5)])
    for pi in available_pi[1:]:
        list_instructions.extend(
            [(pi['mac'], 1, 6),
             (pi['mac'], settings.DEMO_CONSTANTS.session_time, 5)])
    enqueue_instructions(list_instructions, sess_id, delay)
