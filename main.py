import sys
sys.path.append('..')

import lib.rel_algebra_calculus.rel_algebra_calculus as ra
# note: you can use ra.imply(a,b) which expresses a --> b (a implies b)

def ha2(univDB):
    tables = univDB["tables"]
    department = tables["department"]
    course = tables["course"]
    prereq = tables["prereq"]
    # class may be a reserved word - check
    class_ = tables["class"]
    faculty = tables["faculty"]
    student = tables["student"]
    enrollment = tables["enrollment"]
    transcript = tables["transcript"]

    # ---------------------------------------------------------------
    # Your set creater functions or other helper functions (if needed)

    def joinEnrollmentAndBrodskyClassesAndStudent():
        return [
            { **c, **e }
            for c in joinEnrollmentAndBrodskyClasses()
            for e in student
            if c["class"] == e["class"]
        ]
    
    def joinEnrollmentAndBrodskyClasses():
        return [
            { **c, **e }
            for c in getClassesTaughtByBrodskyProjectClass()
            for e in enrollment
            if c["class"] == e["class"]
        ]
    
    def getClassesTaughtByBrodskyProjectClass():
        return [
            { "ssn": s["ssn"]}
            for s in getClassesTaughtByBrodsky()
        ]

    def getClassesTaughtByBrodsky():
        return [
            { **c, **p }
            for c in classTaughtByBrodsky()
            for p in class_
            if c["ssn"] == p["instr"]
        ]

    def classTaughtByBrodsky():
    # s took course (dcode,cno) and received A or B
        result = [
            f
            for f in faculty
            if f["name"] == "Brodsky"
        ]
        return result
    
    def studentTookCS530(s):
        for t in transcript:
            if t["dcode"] == "CS" and t["cno"] == 530  and t["ssn"] == s["ssn"]:
               return True
        return False

    def studSatCourseAB(s, dcode, cno):
    # s took course (dcode,cno) and received A or B
        result = any([
            t["ssn"] == s["ssn"] and
            t["dcode"] == dcode and
            t["cno"] == cno and
            (t["grade"] == "A" or t["grade"] == "B")
            for t in transcript
    ])
        return result

    def studSatPrereqs(s, dcode, cno):
        # s sat'd all prereqs of (dcode,cno)
        # for every prereq (pcode,pno) of (dcode,cno), s sat'd it w/A or B
        result = all([
            #bool cond for a prereq
            studSatCourseAB(s,p["pcode"],p["pno"])
            for p in prereq
            if p["dcode"] == dcode and p["cno"] == cno
        ])
#        print("\n\ns :", s["ssn"], "dcode :", dcode, "cno :", cno, "result :", result)
        return result

    def getCoursePrereqJoin():
        return [
            { **c, **p }
            for c in course
            for p in prereq
            if c["dcode"] == p["dcode"]
            if c["cno"] == p["cno"]
        ]

    def getAllCoursesByDcodeAndCno():
        return [
            {"dcode": c["dcode"], "cno": c["cno"]}
            for c in course
        ]

    def getJoinedCoursePrereqByDcodeAndCno():
        return [
            {"dcode": c["dcode"], "cno": c["cno"]}
            for c in getCoursePrereqJoin()
        ]    

    def getStudentCoursesTakenFromTranscript(s, c):
        result = any([
                t["ssn"] == s["ssn"] and
                t["dcode"] == c["dcode"] and
                t["cno"] == c["cno"]
                for t in transcript
        ])
        return result

    def getAllPrereqCoursesNeeded(co, s):
        result = any([
            e["class"] == c["class"] and
            e["ssn"] == s["ssn"] and
            p["dcode"] == c["dcode"] and
            p["cno"] == c["cno"] and
            p["pcode"] == co["dcode"] and
            p["pno"] == co["cno"]
            for c in class_
            for e in enrollment
            for p in prereq
        ])
        return result

    def getAllMathClasses():
        result = any([
                c["dcode"] == "MTH"
                for c in class_
        ])
        return result

    # ---------------------------------------------------------------
    # Your queries

    # query_a
    query_a = list()
    for s in student:
        if studentTookCS530(s):
            query_a.append(s)

    # query_b
    query_b = list()
    for s in student:
        if studentTookCS530(s) and s["name"] == "John":
            query_b.append(s)

    # query_c
    query_c = ra.distinct([ 
        s
        for s in student
        if all([
           ra.imply(
               getAllPrereqCoursesNeeded(co, s),
               studSatCourseAB(s, co["dcode"], co["cno"])
           )
           for co in course
       ])
    ])

    # query_d
    query_d = [
        s
        for s in student
        if any([
            e["ssn"] == s["ssn"] and
                e["class"] == c["class"] and
                not(studSatPrereqs(s, c["dcode"], c["cno"]))
            for e in enrollment
            for c in class_
        ])
    ]

    # query_e
    query_e = ra.distinct([ 
        s
        for s in student
        if s["name"] == "John"
        if all([
            any([
                e["ssn"] == s["ssn"] and
                e["class"] == c["class"] and
                not(studSatPrereqs(s, c["dcode"], c["cno"]))
                for e in enrollment
                for c in class_
            ])
       ])
    ])   

    # query_f
    query_f = [ 
        s1
        for s1 in getAllCoursesByDcodeAndCno()
        if all([
            s1 != s2
            for s2 in getJoinedCoursePrereqByDcodeAndCno()
        ])
    ]

    # query_g
    query_g = ra.distinct(getJoinedCoursePrereqByDcodeAndCno()) 
    
    # query_h
    query_h = [
        c
        for c in class_
        if  any([
            c["dcode"] == p["dcode"] and c["cno"] == p["cno"] #p is a prereq
            for p in prereq
            #offered this semester and has prereqs
        ])
    ]

    # query_i
    query_i = ra.distinct([ 
        s
        for s in student
        if all([
           ra.imply(
               getStudentCoursesTakenFromTranscript(s, c),
                    studSatCourseAB(s, c["dcode"], c["cno"])
           )
           for c in course
       ])
    ])

    # query_j
    query_j = ra.distinct([
        {"ssn": s["ssn"]}
        for s in student            
        if all([
            #student is enrolled in c
            any([
                e["ssn"] == s["ssn"] and
                e["class"] == c["class"] and 
                e["class"] == b["class"]
                for e in enrollment
                for b in getClassesTaughtByBrodsky()
            ])     
            for c in class_   
        ])  
    ])

    # query_k
    query_k = ra.distinct([
        {"ssn": e["ssn"]}
        for e in enrollment            
        if all([
            #student is enrolled in c
            any([
                e1["ssn"] == e["ssn"] and
                e1["class"] == c["class"]
                for e1 in enrollment   
            ])     
            for c in class_   
        ])  
    ])

    # query_l
    query_l = ra.distinct([
       {"ssn": s["ssn"]}
       for s in student 
       if s["major"] == "CS"
       if any([
           e["ssn"] == s["ssn"]
           for e in enrollment
       ])
       if all([
           ra.imply(getAllMathClasses(),
            any([
                s["ssn"] == e["ssn"] and
                e["class"] == c["class"]
                for e in enrollment   
            ])) 
            for c in class_  
       ])
    ])

    # ---------------------------------------------------------------
    # Some post-processing which you do not need to worry about
    # Do not change anything after this

    ra.sortTable(query_a,["ssn"])
    ra.sortTable(query_a,["ssn"])
    ra.sortTable(query_b,["ssn"])
    ra.sortTable(query_c, ['ssn'])
    ra.sortTable(query_d, ['ssn'])
    ra.sortTable(query_e, ['ssn'])
    ra.sortTable(query_f, ['dcode', 'cno'])
    ra.sortTable(query_g, ['dcode', 'cno'])
    ra.sortTable(query_h, ['class'])
    ra.sortTable(query_i, ['ssn'])
    ra.sortTable(query_j, ['ssn'])
    ra.sortTable(query_k, ['ssn'])
    ra.sortTable(query_l, ['ssn'])

    return({
        "query_a": query_a,
        "query_b": query_b,
        "query_c": query_c,
        "query_d": query_d,
        "query_e": query_e,
        "query_f": query_f,
        "query_g": query_g,
        "query_h": query_h,
        "query_i": query_i,
        "query_j": query_j,
        "query_k": query_k,
        "query_l": query_l,

    })
