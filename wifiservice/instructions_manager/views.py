"""Views for managing instructions.

Instruction ID:
- 0: Shut down all the updates and exit.
- 1: Start probe request mode and start capturing data.
- 2: Stop probe request mode and send captured data.
- 3: Start hotspot mode and start capturing data.
- 4: Stop hotspot mode and send captured data.

Views:
- Get all the instructions as per MAC address
- Post an instruction as per the MAC address
- Post an acknowledgment instruction executed by the MAC address

"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from db_manager.models import get_instructions_collection
import datetime
import traceback
from django.conf import settings


def is_pi_busy(pi):
    """Return True if pi is alive."""
    if (
        pi["is_busy"]
        and (datetime.datetime.now() - pi["updated_at"]).total_seconds()
        > settings.MAX_EXECUTION_TIME
    ):
        return False
    if pi["is_busy"]:
        return True
    return False


def get_pi_instruction_obj(mac_address, get_default=False):
    """Return a new instruction object."""
    instructions_collection = get_instructions_collection()
    pi_instruction_obj = instructions_collection.find_one({"mac": mac_address})
    if not pi_instruction_obj and get_default:
        pi_instruction_obj = dict(
            mac=mac_address,
            instruction_list=[],
            is_busy=False,
            updated_at=datetime.datetime.now(),
        )
    return pi_instruction_obj


def is_instruction_addition_possible(mac_address):
    """Check if instruction addition is possible."""
    pi_instruction_obj = get_pi_instruction_obj(mac_address)
    if pi_instruction_obj and is_pi_busy(pi_instruction_obj):
        return False
    return True


def upsert_pi_instruction_obj(pi_instruction_obj):
    """Update or insert instruction object."""
    instructions_collection = get_instructions_collection()
    pi_instruction_obj["updated_at"] = datetime.datetime.now()
    return instructions_collection.replace_one(
        {"mac": pi_instruction_obj["mac"]}, pi_instruction_obj, upsert=True
    )


def empty_mac_instructions(mac_address):
    """Empty instructions for mac."""
    pi_instruction_obj = get_pi_instruction_obj(mac_address, get_default=True)
    pi_instruction_obj["instruction_list"] = []
    pi_instruction_obj["is_busy"] = False
    upsert_pi_instruction_obj(pi_instruction_obj)
    return pi_instruction_obj


def is_instruction_available(mac_address):
    """Check if instruction is available."""
    pi_instruction_obj = get_pi_instruction_obj(mac_address)
    return bool(
        pi_instruction_obj
        and len(pi_instruction_obj["instruction_list"]) > 0
        and not is_pi_busy(pi_instruction_obj)
    )


def add_instruction_helper(mac, code):
    """Add instruction if possible else return None."""
    if is_instruction_addition_possible(mac):
        pi_instruction_obj = get_pi_instruction_obj(mac, get_default=True)
        if code not in pi_instruction_obj["instruction_list"]:
            pi_instruction_obj["instruction_list"] = [str(code)]
        return upsert_pi_instruction_obj(pi_instruction_obj)
    return None


# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def add_instruction(request):
    """Update status of the pi in mongo."""
    instruction = request.POST.dict()
    try:
        mac = instruction["mac"]
        code = instruction["code"]
        result = add_instruction_helper(mac, code)
        if result:
            return JsonResponse({"ok": result.modified_count})
        else:
            return JsonResponse({"ok": 0, "error": "Device busy."})
    except Exception:
        return HttpResponse(traceback.format_exc(), status=400)


@require_http_methods(["GET"])
def get_instruction_for_execution(request):
    """Get instruction for execution."""
    mac_address = request.GET["mac"]
    if is_instruction_available(mac_address):
        pi_instruction_obj = get_pi_instruction_obj(mac_address, get_default=True)
        pi_instruction_obj["is_busy"] = True
        instruction_code = pi_instruction_obj["instruction_list"][0]
        update_result = upsert_pi_instruction_obj(pi_instruction_obj)
        return JsonResponse(
            {"ok": update_result.matched_count, "code": instruction_code}
        )
    return HttpResponse("Bad request.", status=400)


@csrf_exempt
@require_http_methods(["POST"])
def executed_instruction(request):
    """Acknowledge the instruction is executed."""
    instruction = request.POST.dict()
    try:
        mac = instruction["mac"]
        code = instruction["code"]
        pi_instruction_obj = get_pi_instruction_obj(mac, get_default=True)
        if (
            pi_instruction_obj["is_busy"]
            and pi_instruction_obj["instruction_list"][0] == code
        ):
            pi_instruction_obj["is_busy"] = False
            pi_instruction_obj["instruction_list"].remove(code)
            update_result = upsert_pi_instruction_obj(pi_instruction_obj)
            return JsonResponse({"ok": update_result.matched_count})
        else:
            return JsonResponse({"ok": 0, "error": "Invalid acknowledgement."})
    except Exception:
        return HttpResponse(traceback.format_exc(), status=400)
