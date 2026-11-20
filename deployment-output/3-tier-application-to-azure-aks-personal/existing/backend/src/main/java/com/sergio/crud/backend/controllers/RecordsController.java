package com.sergio.crud.backend.controllers;

import com.sergio.crud.backend.dtos.GymRecordDto;
import com.sergio.crud.backend.services.RecordsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/gym")
@RequiredArgsConstructor
public class RecordsController {

    private final RecordsService recordsService;

    @GetMapping("/records")
    public ResponseEntity<List<GymRecordDto>> allRecords() {
        log.info("GET /api/gym/records - Fetching all gym records");
        List<GymRecordDto> records = recordsService.allRecords();
        log.info("GET /api/gym/records - Returned {} records", records.size());
        return ResponseEntity.ok(records);
    }

    @PostMapping("/records")
    public ResponseEntity<GymRecordDto> createGymRecord(@Valid @RequestBody GymRecordDto recordDto) {
        log.info("POST /api/gym/records - Creating record: exercise={}, weight={}, diet={}",
                recordDto.getExercise(), recordDto.getWeight(), recordDto.getDiet());
        GymRecordDto createdRecord = recordsService.createGymRecords(recordDto);
        log.info("POST /api/gym/records - Created record with id={}", createdRecord.getId());
        return ResponseEntity
                .created(URI.create("/api/gym/records/" + createdRecord.getId()))
                .body(createdRecord);
    }

    @GetMapping("/records/{id}")
    public ResponseEntity<GymRecordDto> getGymRecord(@PathVariable Long id) {
        log.info("GET /api/gym/records/{} - Fetching record", id);
        GymRecordDto record = recordsService.getGymRecord(id);
        log.info("GET /api/gym/records/{} - Found: exercise={}", id, record.getExercise());
        return ResponseEntity.ok(record);
    }

    @PutMapping("/records/{id}")
    public ResponseEntity<GymRecordDto> updateGymRecord(@PathVariable Long id, @Valid @RequestBody GymRecordDto recordDto) {
        log.info("PUT /api/gym/records/{} - Updating record: exercise={}, weight={}, diet={}",
                id, recordDto.getExercise(), recordDto.getWeight(), recordDto.getDiet());
        GymRecordDto updated = recordsService.updateGymRecord(id, recordDto);
        log.info("PUT /api/gym/records/{} - Update successful", id);
        return ResponseEntity.ok(updated);
    }

    @PatchMapping("/records/{id}")
    public ResponseEntity<GymRecordDto> patchGymRecord(@PathVariable Long id, @RequestBody GymRecordDto recordDto) {
        log.info("PATCH /api/gym/records/{} - Partial update: exercise={}, weight={}, diet={}",
                id, recordDto.getExercise(), recordDto.getWeight(), recordDto.getDiet());
        GymRecordDto patched = recordsService.patchGymRecord(id, recordDto);
        log.info("PATCH /api/gym/records/{} - Patch successful", id);
        return ResponseEntity.ok(patched);
    }

    @DeleteMapping("/records/{id}")
    public ResponseEntity<GymRecordDto> deleteGymRecord(@PathVariable Long id) {
        log.info("DELETE /api/gym/records/{} - Deleting record", id);
        GymRecordDto deleted = recordsService.deleteGymRecord(id);
        log.info("DELETE /api/gym/records/{} - Deleted: exercise={}", id, deleted.getExercise());
        return ResponseEntity.ok(deleted);
    }
}
